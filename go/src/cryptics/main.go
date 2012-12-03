package main

import (
	// "cryptics/data_gen"
	// "cryptics/load_utils"
	"bufio"
	"cryptics/solver"
	"cryptics/utils"
	"fmt"
	// "io/ioutil"
	"os"
	"strings"
)

func main() {
	// data_gen.GenerateNgrams()

	// fmt.Println(utils.Anagrams([]string{"pal"}, 3))
	// fmt.Println(solver.TRANSFORMS["syn"]("cat", 10))
	// fmt.Println(solver.SolveFactoredClue([]interface{}{"syn", "cat"}, &utils.Phrasing{Lengths: []int{4}, Pattern: ""}, map[string]map[string]bool{}))
	// fmt.Println(solver.SolveFactoredClue(solver.ParseClue("('clue', ('sub', ('lit', 'significant_ataxia'), ('sub_', 'overshadows')), ('d', 'choral_piece'))"), &, ))
	phrasing := utils.Phrasing{Lengths: []int{7}, Pattern: ""}
	solved_parts := map[string]map[string]bool{}
	fmt.Println("running")
	stdin := bufio.NewReader(os.Stdin)
	var clue string
	for {
		clue, _ = stdin.ReadString('\n')
		if strings.TrimSpace(clue) != "" {
			fmt.Println(solver.FormatAnswers(solver.SolveFactoredClue(solver.ParseClue(clue), &phrasing, solved_parts)))
		}
		// bytes, _ := ioutil.ReadAll(os.Stdin)
		// clues := string(bytes)
		// fmt.Println(clues)
		// for _, clue := range strings.Split(clues, "\n") {
		// }
	}
}
