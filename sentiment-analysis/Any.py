# encoding:utf-8
import codecs
from gensim import corpora
from collections import defaultdict
class Analysis:
    def preteat_clause(self, phase):
        # 分句
        cut_list = list('，。！~？!?…')
        reslist, i, start = [], 0, 0
        for word in phase:
            if word in cut_list:
                reslist.append(phase[start:i])
                start = i + 1
                i += 1
            else:
                i += 1
        if start < len(phase):
            reslist.append(phase[start:])
        return reslist

    # self.move_stopwords(l)
    # for t in l:
    # 	frequency[t] += 1
    #
    # texts = [token for token in frequency if frequency[token] > 0]
    #
    # rtexts = list(set(texts)-set(stropw))
    # return rtexts
    def deal_wrap(self, filedict):
        temp = []
        for x in open(filedict, 'r', encoding='utf-8').readlines():
            temp.append(x.strip())
        return temp
    # 创建停用词list
    def stopwordslist(self, filepath):
        stopwords = [line.strip() for line in codecs.open(filepath, 'r', encoding='utf-8').readlines()]
        return stopwords
    # 对句子去除停用词
    def move_stopwords(self, sentence):
        stopwords = self.stopwordslist(u'F:\Graduationproject\project\dictionary\stopwords.txt')  # 这里加载停用词的路径
        for i in range(len(sentence))[::-1]:
            if sentence[i] in stopwords:
                del sentence[i]
        return sentence

    def sentiment_init(self):
        # 情感词典
        self.posdict = self.deal_wrap('dict/emotion_dict/pos_all_dict.txt')
        self.negdict = self.deal_wrap('dict/emotion_dict/neg_all_dict.txt')
        # 程度副词词典
        self.mostdict = self.deal_wrap('dict/degree_dict/most.txt')  # 权值为2
        self.verydict = self.deal_wrap('dict/degree_dict/very.txt')  # 权值为1.5
        self.moredict = self.deal_wrap('dict/degree_dict/more.txt')  # 权值为1.25
        self.ishdict = self.deal_wrap('dict/degree_dict/ish.txt')  # 权值为0.5
        self.insufficientdict = self.deal_wrap('dict/degree_dict/insufficiently.txt')  # 权值为0.25
        self.inversedict = self.deal_wrap('dict/degree_dict/inverse.txt')  # 权值为-1

    def cal_score(self, word, sentence_score):
        if word in self.mostdict:
            sentence_score *= 2.0
        elif word in self.verydict:
            sentence_score *= 1.75
        elif word in self.moredict:
            sentence_score *= 1.5
        elif word in self.ishdict:
            sentence_score *= 1.2
        elif word in self.insufficientdict:
            sentence_score *= 0.5
        elif word in self.inversedict:
            sentence_score *= -1
        return sentence_score

    def sentiment(self, sentence):
        i, s, posscore, negscore = 0, 0, 0, 0
        for word in sentence:
            if word in self.posdict:
                posscore += 1
                for w in sentence[s:i]:
                    posscore = self.cal_score(w, posscore)
                s = i + 1

            elif word in self.negdict:
                negscore += 1
                for w in sentence[s:i]:
                    negscore = self.cal_score(w, negscore)
                s = i + 1
            i += 1
        return posscore, negscore

    # 生成每个词的子节点字典
    def get_parser_dict(self, words, tuples):
        child_dict = dict()
        tuplelist = tuples[1:]
        for index, arc in enumerate(tuplelist):
            if words[arc[1] - 1] in child_dict:
                tuple = (arc[0], words[arc[-1] - 1])  # 第一个元素是关系，第二个元素是子节点词
                child_dict[words[arc[1] - 1]].append(tuple)
            else:
                child_dict[words[arc[1] - 1]] = []
                tuple = (arc[0], words[arc[-1] - 1])  # 第一个元素是关系，第二个元素是子节点词
                child_dict[words[arc[1] - 1]].append(tuple)
        return child_dict

    # 得到递归子节点字典

    def sentiment_by_rules(self, sentence, dependency):
        posscore, negscore = 0, 0
        deps = self.get_parser_dict(sentence, dependency)
        for word in sentence:
            if word in self.posdict:
                posscore += 1
                if word in deps:
                    for w in deps[word]:
                        posscore = self.cal_score(w[1], posscore)  # w[0]是语句和关系表示，w[1]是子节点词
            elif word in self.negdict:
                negscore += 1
                if word in deps:
                    for w in deps[word]:
                        negscore = self.cal_score(w[1], negscore)

        return posscore, negscore
if __name__ == '__main__':
    sentence = u'虽然生活在一个父母和睦的家庭，他的心中却充满悲伤'
    from stanfordcorenlp import StanfordCoreNLP

    a = Analysis()
    a.sentiment_init()
    total_pscore, total_nscore = 0, 0
    sentence_pscore1, sentence_nscore1 = 0, 0
    with StanfordCoreNLP(r'F:\Graduationproject\stanford-corenlp-full-2016-10-31', lang='zh') as nlp:
        for x in a.preteat_clause(sentence):
            # print(nlp.dependency_parse(sentence))
            # print(nlp.pos_tag(sentence))
            posscore, negscore = a.sentiment_by_rules(nlp.word_tokenize(sentence), nlp.dependency_parse(sentence))
            sentence_pscore1 += posscore
            sentence_nscore1 += negscore

    sentence_pscore, sentence_nscore = 0, 0
    for x in a.preteat_clause(sentence):
        c = a.cutwords_jieba(x, )
        posscore, negscore = a.sentiment(c)
        sentence_pscore += posscore
        sentence_nscore += negscore
    total, right = 0, 0
    with StanfordCoreNLP(r'F:\Graduationproject\stanford-corenlp-full-2016-10-31', lang='zh') as nlp:
        for tempstr in a.deal_wrap('F:\\spider\\trainData\\pos.txt'):
            sentence_pscore, sentence_nscore = 0, 0
            sentence_pscore1, sentence_nscore1 = 0, 0
            for x in a.preteat_clause(tempstr):
                # 传统方法
                c = a.cutwords_jieba(x, )
                posscore, negscore = a.sentiment(c)
                sentence_pscore1 += posscore
                sentence_nscore1 += negscore
                # 依存关系方法
                if x != "":
                    posscore, negscore = a.sentiment_by_rules(nlp.word_tokenize(x), nlp.dependency_parse(x))
                    sentence_pscore += posscore
                    sentence_nscore += negscore
            total_pscore += sentence_pscore
            total_nscore += sentence_nscore
            if sentence_pscore - sentence_nscore != sentence_pscore1 - sentence_nscore1: print(tempstr, '\n',
                                                                                               sentence_pscore1 - sentence_nscore1,
                                                                                               '\n',
                                                                                               sentence_pscore - sentence_nscore)
            if (sentence_pscore > sentence_nscore): right += 1
            total += 1
    print(right, total)
# print('单句：{}得分：\nposscore:{};negscore:{};totalscore:{}\n\n'.format(tempstr,sentence_pscore,sentence_nscore,sentence_pscore-sentence_nscore))
