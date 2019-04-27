import requests,os,json
from sentiment_analysis import Any
from stanfordcorenlp import StanfordCoreNLP
import codecs
def listFile(rootDir):
    list=[]
    for dirpath, dirnames, filenames in os.walk(rootDir):
        for filepath in filenames:
            list.append(os.path.join(dirpath, filepath))
    return list
def wirteFile(filelist,root):#需要扫描统计的文件写入文件中
    with codecs.open(root, 'w', encoding='utf8') as fw:
        for file in filelist:
            fw.write(file.replace('\n',"")+'\n')

def deal_str(str):#return stock code and date
    list=str.split("\\")
    stock_code=list[-2].split("(")[0]
    date=list[-1].split(".")[0]
    return stock_code,date
def statistics(root):
    nlp = StanfordCoreNLP(r'F:\Graduationproject\stanford-corenlp-full-2016-10-31', lang='zh')
    a = Any.Analysis()
    a.sentiment_init()
    with codecs.open("ToBeWritten.txt", 'r', encoding='utf8') as fr:
        filelist = fr.readlines()
    fwriten=codecs.open("AlreadyWritten.txt", 'a+', encoding='utf8')
    try:
        for index,file in enumerate(filelist):
            total, pos, neg, neu = 0, 0, 0, 0
            for tempstr in a.deal_zw(file.replace('\n',"")):
                sentence_pscore, sentence_nscore = 0, 0
                for x in a.preteat_clause(tempstr):
                    # 依存关系方法
                    if x != "":
                        posscore, negscore = a.sentiment_by_rules(nlp.word_tokenize(x), nlp.dependency_parse(x))
                        sentence_pscore += posscore
                        sentence_nscore += negscore
                print(tempstr, '\n', sentence_pscore - sentence_nscore)
                if (sentence_pscore == sentence_nscore): neu += 1
                elif(sentence_pscore > sentence_nscore):pos+=1
                elif(sentence_pscore < sentence_nscore):neg+=1
                total += 1
            stock_code,date=deal_str(file.replace('\n',""))
               # payload = "{\r\n \"stock_code\": \"stock_code\",\r\n\t\t\"date\":\"2018-12-29\",\r\n\t\t\"total_posts\":\"100\",\r\n\t\t\"bullish_num\":\"50\",\r\n\t\t\"bearish_num\":\"50\",\r\n\t\t\"neutral_num\":\"0\",\r\n\t\t\"storage_location\":\"F:\\\\dataClassify\\\\000413(29个）\\\\2018-12-29.txt\"\r\n\t\t\r\n}"
            data={'stock_code':stock_code,
                  'date':date,
                  'total_posts':total,
                  'bullish_num':pos,
                  'bearish_num':neg,
                  'neutral_num':neu,
                  'storage_location':file,
                  }
            headers = {
                'Content-Type': "application/json",
            }
            payload=json.dumps(data)
            response = requests.request("POST", "http://127.0.0.1:8000/statistics/", data=payload, headers=headers)
            filelist.pop(index)
            fwriten.write(file.replace('\n',"")+'\n')
            print(file)
    except:
        wirteFile(filelist,"ToBeWritten.txt")
        fwriten.close()
        nlp.close()
    finally:
        wirteFile(filelist, "ToBeWritten.txt")
        fwriten.close()
        nlp.close()

if __name__ == '__main__':
    statistics("F:\\dataClassify")
    # wirteFile(listFile("F:\\dataClassify"),"ToBeWritten.txt")
