package utils

import (
	"fmt"
	"strings"
)

func Reverse(words []string, phrasing Phrasing) map[string]bool {
	if len(words) > 1 {
		panic("Word must be [1]string: " + fmt.Sprint(words))
	}
	word := strings.ToLower(words[0])
	l := len(word)
	ans := make([]rune, l)
	for i, c := range word {
		ans[l-i-1] = c
	}
	return map[string]bool{string(ans): true}
}

// filter out results with more than one bigram violation. We might allow strings with a bigram violation since they could have letters inserted into them later
func bigram_filter(answers map[string]bool, lengths []int, threshold int) map[string]bool {
	var violations int
	var pass bool
	threshold += len(lengths) - 1 // allow violations across word boundaries

	for ans := range answers {
		violations = 0
		for i := 0; i < len(ans)-1; i++ {
			pass = false
			for _, l := range lengths {
				if NGRAMS[l][ans[i:i+2]] {
					pass = true
					break
				}
			}
			if !pass {
				violations++
				if violations > threshold {
					delete(answers, ans)
					break
				}
			}
		}
	}
	return answers
}

// First 1-3 letters
// last letter
// outside two letters
// inside 1 or 2 letters
// all but first
// all but last
// all but center
// all but edges
func AllLegalSubstrings(words []string, phrasing Phrasing) map[string]bool {
	if len(words) != 1 {
		panic("Word must be [1]string")
	}
	length := Sum(phrasing.Lengths)
	subs := map[string]bool{}
	word := strings.ToLower(words[0])
	if len(word) <= 1 {
		return subs
	}
	if strings.Contains(word, "_") {
		word = strings.Replace(word, "_", "", -1)
	}
	if len(word) > length {
		for i := 0; i < len(word)-length+1; i++ {
			s := word[i : i+length]
			if _, ok := (SYNONYMS)[s]; ok {
				subs[s] = true
			}
		}
	}
	for l := 1; l <= min(len(word)-1, length, 3); l++ {
		subs[word[:l]] = true // first l letters
	}
	subs[word[len(word)-1:]] = true // last letter
	if len(word) > 2 {
		subs[word[:1]+word[len(word)-1:]] = true // outside
		if len(word)%2 == 0 {
			subs[word[len(word)/2-1:len(word)/2+1]] = true         // center
			subs[word[:len(word)/2-1]+word[len(word)/2+1:]] = true // all but center
		} else {
			subs[word[len(word)/2:len(word)/2+1]] = true         // center
			subs[word[:len(word)/2]+word[len(word)/2+1:]] = true // all but center
		}
		subs[word[1:]] = true            // all but first
		subs[word[:len(word)-1]] = true  // all but last
		subs[word[1:len(word)-1]] = true // all but edges
	}
	return bigram_filter(subs, phrasing.Lengths, 1)
}

func min(x ...int) int {
	result := x[0]
	for _, y := range x[1:] {
		if y < result {
			result = y
		}
	}
	return result
}

func AllInsertions(words []string, phrasing Phrasing) map[string]bool {
	if len(words) != 2 {
		panic(fmt.Sprintf("Got wrong number of words. Expected 2, got %d", len(words)))
	}
	word1 := strings.Replace(words[0], "_", "", -1)
	word2 := strings.Replace(words[1], "_", "", -1)
	result := map[string]bool{}
	if word1 == "" || word2 == "" || len(word1)+len(word2) > Sum(phrasing.Lengths) {
		return map[string]bool{}
	}
	// if len(words[0])+len(words[1]) > Sum(phrasing.Lengths) {
	// 	return map[string]bool{}
	// }
	w0, w1 := word1, word2
	for j := 1; j < len(w1); j++ {
		result[w1[0:j]+w0+w1[j:]] = true
	}
	w1, w0 = word1, word2
	for j := 0; j < len(w1); j++ {
		result[w1[0:j]+w0+w1[j:]] = true
	}
	return bigram_filter(result, phrasing.Lengths, 0)
}
