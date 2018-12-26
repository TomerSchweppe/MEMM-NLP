import os
from collections import Counter
from multiprocessing import cpu_count
from main import *
# usage -> python3 generateCompetitionFiles.py

def create_taggers(directory, inference_file):
    """
    create taggers list
    """
    beam_sizes = [5, 5, 5, 10, 5]
    taggers = []
    for idx, filename in enumerate(sorted(os.listdir(directory))):
        if filename.endswith(".pickle"):
            sentences, _ = load_test(inference_file, comp=True)
            viterbi = pickle.load(open(directory+filename, 'rb'))
            taggers.append(parallel_viterbi(viterbi, sentences, beam_sizes[idx], cpu_count())) # todo
    return taggers, sentences


def ensemble_tagger(taggers):
    """
    ensemble taggers to one tagger
    """
    final_tagger = taggers[0]
    for sen_idx in range(len(final_tagger)):
        for tag_idx in range(len(final_tagger[sen_idx])):
            tag_list = []
            for tagger in taggers:
                tag_list.append(tagger[sen_idx][tag_idx])
            cnt = Counter(tag_list)
            final_tagger[sen_idx][tag_idx] = cnt.most_common(1)[0][0]
    return final_tagger


def create_file(inference_file, sentences, tagger):
    """
    create competition file
    """
    if inference_file == 'comp.words':
        f_name = 'comp_m1_203764618.wtag'
    else:
        f_name = 'comp_m2_203764618.wtag'
    fh = open(f_name, 'w')
    for sen_idx, sentence in enumerate(sentences):
        for idx, (word, tag) in enumerate(zip(sentence, tagger[sen_idx])):
            if idx == len(sentence) - 2:
                fh.write(word + '_' + tag)
            elif word != 'STOP' and word != '*':
                fh.write(word + '_' + tag + ' ')
        if sen_idx != len(sentences) - 1:
            fh.write('\n')
    fh.close()


if __name__ == '__main__':

    # create taggers
    comp_taggers, comp_sentences = create_taggers('./cache/comp/', 'comp.words')
    comp2_taggers, comp2_sentences = create_taggers('./cache/comp2/', 'comp2.words')

    # ensemble
    comp_tagger = ensemble_tagger(comp_taggers)
    comp2_tagger = ensemble_tagger(comp2_taggers)

    # create files
    create_file('comp.words', comp_sentences, comp_tagger)
    create_file('comp2.words', comp2_sentences, comp2_tagger)


