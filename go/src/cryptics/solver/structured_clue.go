package solver

import (
	"cryptics/utils"
	"strings"
)

const (
	ANA = iota
	SUB
	REV
	INS
	CAT
	ANA_
	SUB_
	INS_
	REV_
	NULL
	LIT
	DEF
	FIRST
	SYN
)

type clue_function func([]string, utils.Phrasing) map[string]bool

var FUNCTIONS = map[int]clue_function{
	ANA: utils.Anagrams,
	SUB: utils.AllLegalSubstrings,
	REV: utils.Reverse,
	INS: utils.AllInsertions}

var HEADS = map[int]bool{ANA_: true, SUB_: true, INS_: true, REV_: true, DEF: true}

type StructuredClue struct {
	Type int
	Head string
	Args []*StructuredClue
	Ans  map[string][]string // each answer to this clue is a key in the map and each value is the slice of sub-answers to each clue in Args that gave that particular answer
}

func (clue *StructuredClue) Solve(phrasing *utils.Phrasing, solved_parts map[string]map[string][]string, map_c chan bool) (err bool) {
	length := utils.Sum((*phrasing).Lengths)
	var sub_answers map[string][]string
	// fmt.Println("Trying to solve:", clue.HashString())
	<-map_c
	ans, ok := solved_parts[clue.HashString()]
	map_c <- true
	if ok {
		clue.Ans = ans
	} else {
		clue.Ans = map[string][]string{}
		var sub_clue *StructuredClue
		var new_args []string
		trans, trans_ok := TRANSFORMS[clue.Type]
		if HEADS[clue.Type] {
			trans = TRANSFORMS[NULL]
			trans_ok = true
		}
		clue_func, func_ok := FUNCTIONS[clue.Type]
		if trans_ok {
			clue.Ans = trans(clue.Head, length)
		} else if func_ok {
			args_set := [][]string{{}}
			new_args_set := [][]string{}
			for _, sub_clue := range clue.Args {
				err = sub_clue.Solve(phrasing, solved_parts, map_c)
				if err {
					<-map_c
					solved_parts[clue.HashString()] = clue.Ans
					map_c <- true
					return true
				}
				new_args_set = [][]string{}
				for _, args := range args_set {
					sub_answers = sub_clue.Ans
					for sub_ans := range sub_answers {
						new_args = append(args, sub_ans)
						new_args_set = append(new_args_set, new_args)
					}
				}
				args_set = new_args_set
			}
			for _, args := range args_set {
				for sub_ans := range clue_func(filter_empty_strings(args), *phrasing) {
					clue.Ans[sub_ans] = args
				}
			}
		} else if clue.Type == CAT {
			active_set := [][]string{{}}
			new_active_set := [][]string{}
			var candidate []string
			for _, sub_clue = range clue.Args {
				new_active_set = [][]string{}
				err = sub_clue.Solve(phrasing, solved_parts, map_c)
				if err {
					<-map_c
					(solved_parts)[clue.HashString()] = clue.Ans
					map_c <- true
					return true
				}
				for _, s := range active_set {
					for w := range sub_clue.Ans {
						candidate = append(s, strings.Replace(w, "_", "", -1))
						if utils.PartialAnswerTest(strings.Join(candidate, ""), phrasing) {
							new_active_set = append(new_active_set, make([]string, len(candidate)))
							copy(new_active_set[len(new_active_set)-1], candidate)
						}
					}
				}
				if len(new_active_set) > 0 {
					active_set = new_active_set
				} else {
					<-map_c
					(solved_parts)[clue.HashString()] = clue.Ans
					map_c <- true
					return true
				}
			}
			for _, s := range active_set {
				clue.Ans[strings.Join(s, "")] = s
			}
		} else {
			panic("Unrecognized clue type")
		}
	}
	<-map_c
	solved_parts[clue.HashString()] = clue.Ans
	map_c <- true
	_, blank_ans := clue.Ans[""]
	// fmt.Println("returning", clue.Ans, "for clue", clue.HashString())
	if (len(clue.Ans) == 0 || (len(clue.Ans) == 1 && blank_ans)) && (clue.Type != NULL && !HEADS[clue.Type]) {
		// fmt.Println("err true")
		return true
	} else {
		// fmt.Println("err false")
		return false
	}
	return false
}

func (c *StructuredClue) HashString() string {
	result := "(" + type_to_str[c.Type] + ", " + c.Head + ", "
	for _, s := range c.Args {
		result += (s).HashString() + ", "
	}
	result += ")"
	return result
}

func (c *StructuredClue) FormatAnswers() []string {
	var results []string
	var result string
	for ans := range c.Ans {
		result = c.print_with_answer(ans)
		results = append(results, result)
	}
	return results
}

func (c *StructuredClue) print_with_answer(answer string) string {
	var result string
	result = "('" + type_to_str[c.Type] + "', "
	if c.Head != "" {
		result += "'" + c.Head + "', "
	}
	parents := c.Ans[answer]
	if len(parents) > 0 {
		for i, sub_clue := range c.Args {
			result += sub_clue.print_with_answer(parents[i]) + ", "
		}
	}
	result += "'" + strings.ToUpper(answer) + "')"
	return result
}

func filter_empty_strings(input []string) []string {
	result := []string{}
	for _, s := range input {
		if s != "" {
			result = append(result, s)
		}
	}
	return result
}
