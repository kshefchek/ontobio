from ontobio.sim.annotation_scorer import AnnotationScorer
from ontobio.sim.phenosim_engine import PhenoSimEngine
from ontobio.model.similarity import IcStatistic
from ontobio.sim.api.owlsim2 import OwlSim2Api


class TestOwlSimIntegration():
    """
    Hodgepodge of integration tests for ontobio and owlsim2
    to assist in development
    """

    @classmethod
    def setup_class(self):
        self.owlsim2_api = OwlSim2Api()
        self.annot_scorer = AnnotationScorer(self.owlsim2_api)
        self.pheno_sim = PhenoSimEngine(self.owlsim2_api)

    @classmethod
    def teardown_class(self):
        self.annot_scorer = None
        self.pheno_sim = None
        self.owlsim2_api = None

    def test_stat_type(self):
        """
        Test stat type
        """
        assert isinstance(self.owlsim2_api.statistics, IcStatistic)

    def test_fetch_stats(self):
        """
        Test that we're getting stats back and they're the
        correct type
        """
        assert isinstance(self.owlsim2_api.statistics.mean_mean_ic, float)
        assert isinstance(self.owlsim2_api.statistics.individual_count, int)

    def test_fetch_ic(self):
        """
        Fetch two classes that are parent-child
        and test that the child has a higher IC
        than the parent
        :return:
        """
        classes = ['HP:0000739', 'HP:0000740']
        ic_dict = self.owlsim2_api.get_profile_ic(classes)
        assert isinstance(ic_dict['HP:0000740'], float)
        assert ic_dict['HP:0000740'] > ic_dict['HP:0000739']

    def test_get_annotation_suff(self):
        classes = ['HP:0000739', 'HP:0000740']
        negated_classes = []
        annot_suff = self.annot_scorer.get_annotation_sufficiency(classes, negated_classes)
        assert 0 < annot_suff.simple_score < 1
        assert 0 < annot_suff.scaled_score < 1
        assert 0 < annot_suff.categorical_score < 1

    def test_sim_search(self):
        classes = ['HP:0000739', 'HP:0000740']
        search_results = self.pheno_sim.search(classes)
        assert search_results.matches[0].rank == 1
        assert 0 < search_results.matches[0].score < 100
        assert search_results.matches[0].type in ['gene', 'phenotype', 'disease']
        assert search_results.matches[0].taxon.id is not None
        assert len(search_results.matches[0].pairwise_match) > 0
        assert search_results.matches[0].pairwise_match[0].lcs.IC > 0