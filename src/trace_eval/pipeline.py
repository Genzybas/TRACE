"""
TRACE Pipeline Orchestrator.

End-to-end evaluation pipeline coordinating Evidence Acquisition, Behaviour
Interpretation, Behaviour Assessment, and Decision Support.

Pipeline Phase:
    ObservableEvidence -> BehaviourTrace -> BehaviourVector -> BehaviourProfile
    -> BehaviourConfidence -> BehaviourSignature -> TRACE Score
"""

from typing import List, Mapping, Optional, Sequence

from trace_eval.assessment.confidence import BehaviourConfidenceEstimator
from trace_eval.assessment.signature import BehaviourSignature, GlobalCategoryWeights
from trace_eval.domain.profile import BehaviourProfile, CategoryWeights
from trace_eval.domain.trace import BehaviourTrace
from trace_eval.domain.vector import BehaviourVector, NormalizedBehaviourVector
from trace_eval.interpretation.extractor import BaseFeatureExtractor, DefaultBehaviourFeatureExtractor


class TRACEPipeline:
    """
    Main evaluation pipeline executing multidimensional assessment over agent traces.
    """

    def __init__(
        self,
        extractor: Optional[BaseFeatureExtractor] = None,
        confidence_estimator: Optional[BehaviourConfidenceEstimator] = None,
        category_weights: Optional[CategoryWeights] = None,
        global_weights: Optional[GlobalCategoryWeights] = None,
        min_bounds: Optional[Mapping[str, float]] = None,
        max_bounds: Optional[Mapping[str, float]] = None,
    ):
        self.extractor = extractor or DefaultBehaviourFeatureExtractor()
        self.confidence_estimator = confidence_estimator or BehaviourConfidenceEstimator()
        self.category_weights = category_weights or CategoryWeights()
        self.global_weights = global_weights or GlobalCategoryWeights()
        self.min_bounds = min_bounds or {}
        self.max_bounds = max_bounds or {}

    def evaluate_single_trace(self, trace: BehaviourTrace) -> BehaviourProfile:
        """
        Run pipeline for a single BehaviourTrace up to BehaviourProfile.
        """
        raw_vector: BehaviourVector = self.extractor.extract(trace)
        norm_vector: NormalizedBehaviourVector = raw_vector.normalize(
            self.min_bounds, self.max_bounds
        )
        return BehaviourProfile.from_normalized_vector(norm_vector, self.category_weights)

    def evaluate_agent_runs(self, traces: Sequence[BehaviourTrace]) -> BehaviourSignature:
        """
        Run end-to-end pipeline across N repeated trace runs for a given agent.
        Computes Behavioural Confidence \kappa and outputs the final BehaviourSignature.
        """
        if not traces:
            raise ValueError("Trace sequence cannot be empty for agent evaluation.")

        raw_vectors: List[BehaviourVector] = [self.extractor.extract(tr) for tr in traces]
        normalized_vectors: List[NormalizedBehaviourVector] = [
            vec.normalize(self.min_bounds, self.max_bounds) for vec in raw_vectors
        ]
        profiles: List[BehaviourProfile] = [
            BehaviourProfile.from_normalized_vector(vec, self.category_weights)
            for vec in normalized_vectors
        ]

        # Compute average profile metrics across N runs
        avg_cognitive = sum(p.cognitive for p in profiles) / len(profiles)
        avg_operational = sum(p.operational for p in profiles) / len(profiles)
        avg_reliability = sum(p.reliability for p in profiles) / len(profiles)

        avg_profile = BehaviourProfile(
            trace_id=f"aggregated_{traces[0].agent_id}",
            agent_id=traces[0].agent_id,
            cognitive=avg_cognitive,
            operational=avg_operational,
            reliability=avg_reliability,
        )

        # Compute Behavioural Confidence \kappa
        # Confidence must be computed on a common, bounded feature scale. Raw
        # event rates and latency-derived values otherwise dominate distance.
        confidence_vectors = [
            BehaviourVector(trace_id=vec.trace_id, agent_id=vec.agent_id, features=vec.normalized_features)
            for vec in normalized_vectors
        ]
        kappa = self.confidence_estimator.compute_confidence(confidence_vectors)

        return BehaviourSignature.create(avg_profile, kappa)
