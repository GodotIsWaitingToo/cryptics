package solver

import (
	"cryptics/utils"
	// "fmt"
)

type transform func(string, int) map[string]bool
type clue_function func([]string, int) map[string]bool

func string_hash(clue []interface{}) string {
	result := "("
	for _, c := range clue {
		switch v := c.(type) {
		case string:
			result += v + ", "
		default:
			result += string_hash(c.([]interface{})) + ", "
		}
	}
	result += ")"
	return result
}

var FUNCTIONS map[string]clue_function = map[string]clue_function{"ana": utils.Anagrams, "sub": utils.AllLegalSubstrings, "rev": utils.Reverse, "ins": utils.AllInsertions}

var TRANSFORMS map[string]transform = map[string]transform{"lit": func(x string, l int) map[string]bool {
	return map[string]bool{x: true}
}, "null": func(x string, l int) map[string]bool {
	return map[string]bool{"": true}
}, "d": func(x string, l int) map[string]bool {
	return map[string]bool{"": true}
}, "first": func(x string, l int) map[string]bool {
	return map[string]bool{string(x[0]): true}
}, "syn": func(x string, l int) map[string]bool {
	if syns, ok := (utils.SYNONYMS)[x]; ok {
		if l == 0 {
			panic("Got zero length")
		}
		result := map[string]bool{}
		for _, s := range syns {
			if len(s) <= l {
				result[s] = true
			}
		}
		return result
	}
	return map[string]bool{}
}}

var HEADS = map[string]bool{"ana_": true, "sub_": true, "ins_": true, "rev_": true}

func SolveFactoredClue(clue []interface{}, phrasing *utils.Phrasing, solved_parts map[string]map[string]bool) map[string]bool {
	candidates, _ := solve_partial_clue(clue, phrasing, solved_parts)
	// fmt.Println(candidates)
	results := map[string]bool{}
	for a := range candidates {
		if utils.AnswerTest(a, phrasing) {
			results[a] = true
		}
	}
	return results
}

func solve_partial_clue(clue []interface{}, phrasing *utils.Phrasing, solved_parts map[string]map[string]bool) (map[string]bool, bool) {
	length := utils.Sum((*phrasing).Lengths)
	var result map[string]bool
	var sub_answers map[string]bool
	var err bool
	var sub_ans string
	var s []string
	// fmt.Println("Trying to solve:", clue)
	if ans, ok := solved_parts[string_hash(clue)]; ok {
		result = ans
		// fmt.Println("Cache hit")
	} else {
		// fmt.Println("Cache miss")
		trans, trans_ok := TRANSFORMS[clue[0].(string)]
		clue_func, func_ok := FUNCTIONS[clue[0].(string)]
		if trans_ok {
			result = trans(clue[1].(string), length)
		} else if func_ok {
			result = map[string]bool{}
			active_set := [][]string{{}}
			var new_active_set [][]string
			var sub_clue []interface{}
			for _, sub_part := range clue[1:len(clue)] {
				sub_clue = sub_part.([]interface{})
				if _, ok := HEADS[sub_clue[0].(string)]; ok {
					continue
				}
				new_active_set = [][]string{}
				for _, s = range active_set {
					sub_answers, err = solve_partial_clue(sub_clue, phrasing, solved_parts)
					if err {
						(solved_parts)[string_hash(clue)] = result
						return result, true
					}
					for sub_ans = range sub_answers {
						new_active_set = append(new_active_set, append(s, sub_ans))
					}
				}
				active_set = new_active_set
			}
			for _, arg_set := range active_set {
				for sub_ans = range clue_func(arg_set, length) {
					result[sub_ans] = true
				}
			}
		} else if clue[0].(string) == "clue" {
			member_test := func(x string) bool {
				return utils.PartialAnswerTest(x, phrasing)
			}
			all_sub_answers := []map[string]bool{}
			var sub_clue []interface{}
			for _, sub_part := range clue[1:len(clue)] {
				sub_clue = sub_part.([]interface{})
				sub_answers, err = solve_partial_clue(sub_clue, phrasing, solved_parts)
				all_sub_answers = append(all_sub_answers, sub_answers)
				if err {
					(solved_parts)[string_hash(clue)] = result
					return result, true
				}
			}
			result = utils.StringTreeSearch(all_sub_answers, member_test)
		} else {
			// fmt.Println("Got this clue type: ", clue[0])
			panic("Unrecognized clue type")
		}
	}
	(solved_parts)[string_hash(clue)] = result
	if len(result) == 1 && result[""] == true && (clue[0].(string) != "null" && clue[0].(string) != "d") {
		return result, true
	} else {
		return result, false
	}
	// fmt.Println("Returning: ", result, " for clue: ", clue)
	return result, false
}
