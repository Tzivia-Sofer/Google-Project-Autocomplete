from collections import defaultdict
import os
import string

num_of_matches = 5

sentences_list = []
source_list = []


class AutoCompleteData:
    def __init__(self, completed_sentence: str, source_text: str, offset: int, score: int):
        self.completed_sentence = completed_sentence
        self.source_text = source_text
        self.offset = offset
        self.score = score

    def get_output(self) -> str:
        return self.completed_sentence.lstrip() + "\n     from source: " + self.source_text + "   offset: " + str(
            self.offset)


def switch_change(index_of_mistake, basic_score):
    switcher = {
        0: basic_score - 5,
        1: basic_score - 4,
        2: basic_score - 3,
        3: basic_score - 2,
    }
    return switcher.get(index_of_mistake, basic_score - 1)


def switch_add_remove(index_of_mistake, basic_score):
    switcher = {
        0: basic_score - 10,
        1: basic_score - 8,
        2: basic_score - 6,
        3: basic_score - 4,
    }
    return switcher.get(index_of_mistake, basic_score - 2)


def remove_punctuation(sentence: str, punt_to_remove: list) -> str:
    return "".join(c for c in sentence if c not in punt_to_remove)


def get_score(whole_sentence, substring, index_of_mistake=-1, changed_letter=False):
    if remove_punctuation(whole_sentence, [',', '.', ' ', '\n']).find(substring) != -1:
        return len(substring) * 2

    # score the string according to the mistake
    return switch_change(index_of_mistake, len(substring) * 2) if changed_letter else switch_add_remove(
        index_of_mistake, len(substring) * 2)





def update_high_matches(high_matches_list: list, current_match_index, sub_string, score):
    # prevent duplications
    if current_match_index in high_matches_list:
        return

    # if we don't have enough matches yet, insert current score
    if len(high_matches_list) < num_of_matches:
        high_matches_list.append(current_match_index)


    # else check if current match has higher score
    else:
        # init min score with first element's score
        min_score = get_score(sentences_list[high_matches_list[0]], sub_string)
        match_with_min_score = high_matches_list[0]

        # iterate over matches list to get the match with min score
        for match in high_matches_list:
            current_score = get_score(sentences_list[match], sub_string)
            if current_score < min_score:
                min_score = current_score
                match_with_min_score = match

        # check current match according to it's score, if has to be in high matches list
        if score > min_score:
            high_matches_list.remove(match_with_min_score)
            high_matches_list.append(current_match_index)

        elif score == min_score:
            if sentences_list[current_match_index] < sentences_list[match_with_min_score]:
                high_matches_list.remove(match_with_min_score)
                high_matches_list.append(current_match_index)


def add_to_dict(data, sentence: str, index_in_sentences_list):
    for i in range(3, len(sentence)):
        for j in range(i + 1, len(sentence) + 1):
            score = get_score(sentence, sentence[i:j])
            update_high_matches(data[sentence[i:j]], index_in_sentences_list, sentence[i:j], score)


def updade_matches_with_mistakes(data: dict, high_matches: list, input_, wrong_input, index_of_mistake,
                                 changed_letter: bool):
    # if wrong input exists in data, means it has matches
    if data[wrong_input]:

        score = get_score(input_, wrong_input, index_of_mistake, True) if changed_letter else get_score(
            input_, wrong_input, index_of_mistake, False)

        # iterate over the wrong input matches
        for high_match_index in data[wrong_input]:
            update_high_matches(high_matches, high_match_index, wrong_input, score)


def find_match(data: dict, input_: str) -> list:
    # allow user change upper and lower case, absent or additional character
    letters = list(string.ascii_lowercase) + list(string.ascii_uppercase) + [""]
    high_matches = []

    for i, char in enumerate(input_):
        for letter in letters:
            replaced_input = input_[:i] + letter + input_[i + 1:]
            char_added_input = input_[:i] + letter + input_[i:]
            updade_matches_with_mistakes(data, high_matches, input_, replaced_input, i, True)
            updade_matches_with_mistakes(data, high_matches, input_, char_added_input, i, False)

    return high_matches


def not_empty(line) -> bool:
    return remove_punctuation(line, [',', '.', ' ', '\n']) != ''


def read_file(path: str):
    # read file line by line and init the sentences lists and sources list .
    with open(path, encoding="utf8") as file:
        for line_number, line in enumerate(file):
            # check if line is not empty
            if not_empty(line):
                sentences_list.append(remove_punctuation(line, ['\n']))
                source_list.append(path + " Line: " + str(line_number))


def read_all_files():
    for root, dirs, files in os.walk('./python-3.8.4-docs-text', topdown=True):
        for file in files:
            if file.endswith(".txt"):
                read_file(os.path.join(root, file))


def built_dict() -> dict:
    data = defaultdict(list)
    for index_in_sentences_list, sentence in enumerate(sentences_list):
        add_to_dict(data, remove_punctuation(sentence, [',', '.', ' ', '\n']), index_in_sentences_list)
    return data


def init_data_base() -> dict:
    read_all_files()
    data = built_dict()
    return data


def get_len_long_substr(str1, str2):
    substring = ''
    len_str1 = len(str1)
    idx1 = -1
    idx2 = -1
    if len_str1 > 0:
        for i in range(len_str1):
            for j in range(len_str1 - i + 1):
                if j > len(substring) and all(str1[i:i + j] in x for x in [str1, str2]):
                    substring = str1[i:i + j]

        idx1 = str1.index(substring)
        idx2 = str2.index(substring)

    return idx1, idx2, len(substring)

def sort_by_score(user_input: str, result: list) -> dict:

    scores_dict = {}
    for high_match_index in result:
        idx_in_sentence, idx_in_substring, max_sub_string = get_len_long_substr(sentences_list[high_match_index],user_input)
        if idx_in_substring == 0 :
            if max_sub_string == len(user_input):
                score = get_score(sentences_list[high_match_index], user_input)
            else:
                score = get_score(sentences_list[high_match_index],user_input, max_sub_string)
        else:
            score = get_score(sentences_list[high_match_index], user_input, idx_in_substring)

        scores_dict[high_match_index] = score

    return scores_dict



def get_offset(sentence, sub_string) -> int:
    idx_in_sentence, idx_in_substring, max_sub_string = get_len_long_substr(sentence, sub_string)
    return idx_in_sentence if idx_in_substring == 0 else idx_in_sentence - idx_in_substring


def auto_complete(user_input: str) -> list:
    if user_input.find('#') != -1:
        return []

    auto_complete_list = []
    result = find_match(data, remove_punctuation(user_input, [',', '.', ' ', '\n']))
    scoers_dict = sort_by_score(user_input,result)

    result = [k for k, v in sorted(scoers_dict.items(), key=lambda item: item[1])]

    if len(result) == 0:
        print("No Matches...")

    else:
        for ind, sentence_index in enumerate(result):
            offset = get_offset(sentences_list[sentence_index], user_input)
            auto_complete_data = AutoCompleteData(sentences_list[sentence_index], source_list[sentence_index], offset,
                                                  get_score(sentences_list[sentence_index], user_input))
            auto_complete_list.append(auto_complete_data)
            print(ind + 1, ". ", auto_complete_data.get_output())

    return auto_complete_list


if __name__ == "__main__":

    print("Loading system...")
    data = init_data_base()

    user_input = input("The system is ready, enter your text: \n")

    while True:
        if len(user_input) > 2:
            auto_complete(user_input)
        if user_input.find('#') != -1:
            user_input = input("Enter input: ")
        else:
            user_input += input(user_input)
