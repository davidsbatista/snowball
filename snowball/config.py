__author__ = "David S. Batista"
__email__ = "dsbatista@gmail.com"

import fileinput
import pickle

from nltk.corpus import stopwords

from snowball.reverb_breds import Reverb
from snowball.seed import Seed
from snowball.vector_space_model import VectorSpaceModel


class Config:
    # pylint: disable=too-many-instance-attributes
    """
    Configuration class
    """

    def __init__(self, config_file, seeds_file, negative_seeds, sentences_file, similarity, confidence):
        # pylint: disable=too-many-arguments, too-many-statements, too-many-branches
        self.seed_tuples = set()
        self.negative_seed_tuples = set()
        self.e1_type = None
        self.e2_type = None
        self.stopwords = stopwords.words("english")
        self.threshold_similarity = similarity
        self.instance_confidence = confidence
        self.reverb = Reverb()

        for line in fileinput.input(config_file):
            if line.startswith("#") or len(line) == 1:
                continue

            if line.startswith("wUpdt"):
                self.w_updt = float(line.split("=")[1])

            if line.startswith("wUnk"):
                self.w_unk = float(line.split("=")[1])

            if line.startswith("wNeg"):
                self.w_neg = float(line.split("=")[1])

            if line.startswith("number_iterations"):
                self.number_iterations = int(line.split("=")[1])

            if line.startswith("use_RlogF"):
                self.use_r_log_f = bool(line.split("=")[1])

            if line.startswith("min_pattern_support"):
                self.min_pattern_support = int(line.split("=")[1])

            if line.startswith("max_tokens_away"):
                self.max_tokens_away = int(line.split("=")[1])

            if line.startswith("min_tokens_away"):
                self.min_tokens_away = int(line.split("=")[1])

            if line.startswith("context_window_size"):
                self.context_window_size = int(line.split("=")[1])

            if line.startswith("use_reverb"):
                self.use_reverb = line.split("=")[1].strip()

            if line.startswith("alpha"):
                self.alpha = float(line.split("=")[1])

            if line.startswith("beta"):
                self.beta = float(line.split("=")[1])

            if line.startswith("gamma"):
                self.gamma = float(line.split("=")[1])

        assert self.alpha + self.beta + self.gamma == 1

        self.read_seeds(seeds_file)
        self.read_negative_seeds(negative_seeds)
        fileinput.close()

        print("\nConfiguration parameters")
        print("========================")
        print("e1 type              :", self.e1_type)
        print("e2 type              :", self.e2_type)
        print("context window       :", self.context_window_size)
        print("max tokens away      :", self.max_tokens_away)
        print("min tokens away      :", self.min_tokens_away)
        print("use ReVerb           :", self.use_reverb)
        print("")
        print("alpha                :", self.alpha)
        print("beta                 :", self.beta)
        print("gamma                :", self.gamma)
        print("")
        print("positive seeds       :", len(self.seed_tuples))
        print("negative seeds       :", len(self.negative_seed_tuples))
        print("negative seeds wNeg  :", self.w_neg)
        print("unknown seeds wUnk   :", self.w_unk)
        print("")
        print("threshold_similarity :", self.threshold_similarity)
        print("instance confidence  :", self.instance_confidence)
        print("min_pattern_support  :", self.min_pattern_support)
        print("iterations           :", self.number_iterations)
        print("iteration wUpdt      :", self.w_updt)
        print("\n")

        try:
            print("\nLoading tf-idf model from disk...")
            with open("vsm.pkl", "rb") as f_in:
                self.vsm = pickle.load(f_in)

        except IOError:
            print("\nGenerating tf-idf model from sentences...")
            self.vsm = VectorSpaceModel(sentences_file, self.stopwords)
            print("\nWriting generated model to disk...")
            with open("vsm.pkl", "wb") as f_out:
                pickle.dump(self.vsm, f_out)

    def read_seeds(self, seeds_file):
        """
        Read seeds from file
        """
        for line in fileinput.input(seeds_file):
            if line.startswith("#") or len(line) == 1:
                continue
            if line.startswith("e1"):
                self.e1_type = line.split(":")[1].strip()
            elif line.startswith("e2"):
                self.e2_type = line.split(":")[1].strip()
            else:
                ent1 = line.split(";")[0].strip()
                ent2 = line.split(";")[1].strip()
                self.seed_tuples.add(Seed(ent1, ent2))

    def read_negative_seeds(self, negative_seeds):
        """
        Read negative seeds from file
        """
        for line in fileinput.input(negative_seeds):
            if line.startswith("#") or len(line) == 1:
                continue
            if line.startswith("e1"):
                self.e1_type = line.split(":")[1].strip()
            elif line.startswith("e2"):
                self.e2_type = line.split(":")[1].strip()
            else:
                ent1 = line.split(";")[0].strip()
                ent2 = line.split(";")[1].strip()
                self.negative_seed_tuples.add(Seed(ent1, ent2))
