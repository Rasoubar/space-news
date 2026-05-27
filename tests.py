import engine as e
import scraper as s
import config
from utils import vectorize_texts, calc_similarity


def test_date():
    for source,url in config.feeds.items():
        print(url)
        for entry in s.feed_extraction(url):
            print(e.read_rss_entry(entry,source)["date_string"])

def test_ivy():
    text1= "Diapsids show an extremely wide range of reproductive strategies. Offspring may receive no parental care, care from only one sex, care from both parents, or care under more complex regimes. Young may vary from independent, super-precocial hatchlings to altricial neonates needing much care before leaving the nest. Parents can invest heavily in a few young, or less so in a larger number. Here we examine the evolution of these traits across a composite phylogeny spanning the extant diapsids and including the limited number of extinct taxa for which reproductive strategies can be well constrained. Generalized estimating equation(GEE)-based phylogenetic comparative methods demonstrate the influences of body mass, parental care strategy and hatchling maturity on clutch volume across the diapsids. The influence of polygamous reproduction is not important despite a large sample size. Applying the results of these models to the dinosaurs supports the hypothesis of paternal care (male only) in derived non-avian theropods, previously suggested based on simpler analyses. These data also suggest that sauropodomorphs did not care for their young. The evolution of parental-care occurs in an almost linear series of transitions. Paternal care rarely gives rise to other care strategies. Where hatchling condition changes, diapsids show an almost unidirectional tendency of evolution towards increased altriciality. Transitions to social monogamy from the ancestral state in diapsids, where both sexes are polygamous, are common. In contrast, once evolved, polygyny and polyandry are very evolutionarily stable. Polygyny and maternal care correlate, as do polyandry and paternal care. Ancestral-character estimation (ACE) of these care strategies with the character transition likelihoods estimated from the original data gives good confidence at most important nodes. These analyses suggest that the basalmost diapsids had no parental care. Crocodilians independently evolved maternal care, paternal care evolved in the saurischian line, prior to derived theropod dinosaurs, and the most basal neognaths likely exhibited biparental care. Overall, the evolution of parental care among diapsids shows a persistent trend towards increased care of offspring, and more complex care strategies and behaviors with time. Reversions to reduced care are infrequent."
    text2= "Cars are multiplying and their rate of productios progress might go like"
    vector1 = vectorize_texts(text1)
    vector2 = vectorize_texts(text2)
    result = calc_similarity(vector1, [vector2])
    print(result)

