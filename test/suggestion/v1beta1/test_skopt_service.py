# Copyright 2021 The Kubeflow Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import grpc
import grpc_testing

from pkg.apis.manager.v1beta1.python import api_pb2
from pkg.suggestion.v1beta1.skopt.service import SkoptService


class TestSkopt(unittest.TestCase):
    def setUp(self):
        servicers = {
            api_pb2.DESCRIPTOR.services_by_name['Suggestion']: SkoptService(
            )
        }

        self.test_server = grpc_testing.server_from_dictionary(
            servicers, grpc_testing.strict_real_time())

    def test_get_suggestion(self):
        trials = [
            api_pb2.Trial(
                name="test-asfjh",
                spec=api_pb2.TrialSpec(
                    objective=api_pb2.ObjectiveSpec(
                        type=api_pb2.MAXIMIZE,
                        objective_metric_name="metric-2",
                        goal=0.9
                    ),
                    parameter_assignments=api_pb2.TrialSpec.ParameterAssignments(
                        assignments=[
                            api_pb2.ParameterAssignment(
                                name="param-1",
                                value="2",
                            ),
                            api_pb2.ParameterAssignment(
                                name="param-2",
                                value="cat1",
                            ),
                            api_pb2.ParameterAssignment(
                                name="param-3",
                                value="2",
                            ),
                            api_pb2.ParameterAssignment(
                                name="param-4",
                                value="3.44",
                            )
                        ]
                    )
                ),
                status=api_pb2.TrialStatus(
                    observation=api_pb2.Observation(
                        metrics=[
                            api_pb2.Metric(
                                name="metric=1",
                                value="435"
                            ),
                            api_pb2.Metric(
                                name="metric=2",
                                value="5643"
                            ),
                        ]
                    )
                )
            ),
            api_pb2.Trial(
                name="test-234hs",
                spec=api_pb2.TrialSpec(
                    objective=api_pb2.ObjectiveSpec(
                        type=api_pb2.MAXIMIZE,
                        objective_metric_name="metric-2",
                        goal=0.9
                    ),
                    parameter_assignments=api_pb2.TrialSpec.ParameterAssignments(
                        assignments=[
                            api_pb2.ParameterAssignment(
                                name="param-1",
                                value="3",
                            ),
                            api_pb2.ParameterAssignment(
                                name="param-2",
                                value="cat2",
                            ),
                            api_pb2.ParameterAssignment(
                                name="param-3",
                                value="6",
                            ),
                            api_pb2.ParameterAssignment(
                                name="param-4",
                                value="4.44",
                            )
                        ]
                    )
                ),
                status=api_pb2.TrialStatus(
                    observation=api_pb2.Observation(
                        metrics=[
                            api_pb2.Metric(
                                name="metric=1",
                                value="123"
                            ),
                            api_pb2.Metric(
                                name="metric=2",
                                value="3028"
                            ),
                        ]
                    )
                )
            )
        ]
        experiment = api_pb2.Experiment(
            name="test",
            spec=api_pb2.ExperimentSpec(
                algorithm=api_pb2.AlgorithmSpec(
                    algorithm_name="bayesianoptimization",
                    algorithm_settings=[
                        api_pb2.AlgorithmSetting(
                            name="random_state",
                            value="10"
                        )
                    ],
                ),
                objective=api_pb2.ObjectiveSpec(
                    type=api_pb2.MAXIMIZE,
                    goal=0.9
                ),
                parameter_specs=api_pb2.ExperimentSpec.ParameterSpecs(
                    parameters=[
                        api_pb2.ParameterSpec(
                            name="param-1",
                            parameter_type=api_pb2.INT,
                            feasible_space=api_pb2.FeasibleSpace(
                                max="5", min="1", list=[]),
                        ),
                        api_pb2.ParameterSpec(
                            name="param-2",
                            parameter_type=api_pb2.CATEGORICAL,
                            feasible_space=api_pb2.FeasibleSpace(
                                max=None, min=None, list=["cat1", "cat2", "cat3"])
                        ),
                        api_pb2.ParameterSpec(
                            name="param-3",
                            parameter_type=api_pb2.DISCRETE,
                            feasible_space=api_pb2.FeasibleSpace(
                                max=None, min=None, list=["3", "2", "6"])
                        ),
                        api_pb2.ParameterSpec(
                            name="param-4",
                            parameter_type=api_pb2.DOUBLE,
                            feasible_space=api_pb2.FeasibleSpace(
                                max="5", min="1", list=[])
                        )
                    ]
                )
            )
        )

        request = api_pb2.GetSuggestionsRequest(
            experiment=experiment,
            trials=trials,
            request_number=2,
        )

        get_suggestion = self.test_server.invoke_unary_unary(
            method_descriptor=(api_pb2.DESCRIPTOR
                .services_by_name['Suggestion']
                .methods_by_name['GetSuggestions']),
            invocation_metadata={},
            request=request, timeout=1)

        response, metadata, code, details = get_suggestion.termination()
        print(response.parameter_assignments)
        self.assertEqual(code, grpc.StatusCode.OK)
        self.assertEqual(2, len(response.parameter_assignments))

    def test_validate_algorithm_settings(self):
        experiment_spec = [None]

        def call_validate():
            experiment = api_pb2.Experiment(name="test", spec=experiment_spec[0])
            request = api_pb2.ValidateAlgorithmSettingsRequest(experiment=experiment)

            validate_algorithm_settings = self.test_server.invoke_unary_unary(
                method_descriptor=(api_pb2.DESCRIPTOR
                    .services_by_name['Suggestion']
                    .methods_by_name['ValidateAlgorithmSettings']),
                invocation_metadata={},
                request=request, timeout=1)

            return validate_algorithm_settings.termination()

        # valid cases
        algorithm_spec = api_pb2.AlgorithmSpec(
            algorithm_name="bayesianoptimization",
            algorithm_settings=[
                api_pb2.AlgorithmSetting(
                    name="random_state",
                    value="10"
                )
            ],
        )
        experiment_spec[0] = api_pb2.ExperimentSpec(algorithm=algorithm_spec)
        self.assertEqual(call_validate()[2], grpc.StatusCode.OK)

        # invalid cases
        # unknown algorithm name
        experiment_spec[0] = api_pb2.ExperimentSpec(
            algorithm=api_pb2.AlgorithmSpec(algorithm_name="unknown"))
        _, _, code, details = call_validate()
        self.assertEqual(code, grpc.StatusCode.INVALID_ARGUMENT)
        self.assertEqual(details, 'unknown algorithm name unknown')

        # unknown config name
        experiment_spec[0] = api_pb2.ExperimentSpec(
            algorithm=api_pb2.AlgorithmSpec(
                algorithm_name="bayesianoptimization",
                algorithm_settings=[
                    api_pb2.AlgorithmSetting(name="unknown_conf", value="1111")]
            ))
        _, _, code, details = call_validate()
        self.assertEqual(code, grpc.StatusCode.INVALID_ARGUMENT)
        self.assertEqual(details, 'unknown setting unknown_conf for algorithm bayesianoptimization')

        # unknown base_estimator
        experiment_spec[0] = api_pb2.ExperimentSpec(
            algorithm=api_pb2.AlgorithmSpec(
                algorithm_name="bayesianoptimization",
                algorithm_settings=[
                    api_pb2.AlgorithmSetting(name="base_estimator", value="unknown estimator")]
            ))
        _, _, code, details = call_validate()
        wrong_algorithm_setting = experiment_spec[0].algorithm.algorithm_settings[0]
        self.assertEqual(code, grpc.StatusCode.INVALID_ARGUMENT)
        self.assertEqual(details,
                         "{name} {value} is not supported in Bayesian optimization".format(
                             name=wrong_algorithm_setting.name,
                             value=wrong_algorithm_setting.value))

        # wrong n_initial_points
        experiment_spec[0] = api_pb2.ExperimentSpec(
            algorithm=api_pb2.AlgorithmSpec(
                algorithm_name="bayesianoptimization",
                algorithm_settings=[
                    api_pb2.AlgorithmSetting(name="n_initial_points", value="-1")]
            ))
        _, _, code, details = call_validate()
        wrong_algorithm_setting = experiment_spec[0].algorithm.algorithm_settings[0]
        self.assertEqual(code, grpc.StatusCode.INVALID_ARGUMENT)
        self.assertEqual(details, "{name} should be great or equal than zero".format(name=wrong_algorithm_setting.name))

        # unknown acq_func
        experiment_spec[0] = api_pb2.ExperimentSpec(
            algorithm=api_pb2.AlgorithmSpec(
                algorithm_name="bayesianoptimization",
                algorithm_settings=[
                    api_pb2.AlgorithmSetting(name="acq_func", value="unknown")]
            ))
        _, _, code, details = call_validate()
        wrong_algorithm_setting = experiment_spec[0].algorithm.algorithm_settings[0]
        self.assertEqual(code, grpc.StatusCode.INVALID_ARGUMENT)
        self.assertEqual(details,
                         "{name} {value} is not supported in Bayesian optimization".format(
                             name=wrong_algorithm_setting.name,
                             value=wrong_algorithm_setting.value
                         ))

        # unknown acq_optimizer
        experiment_spec[0] = api_pb2.ExperimentSpec(
            algorithm=api_pb2.AlgorithmSpec(
                algorithm_name="bayesianoptimization",
                algorithm_settings=[
                    api_pb2.AlgorithmSetting(name="acq_optimizer", value="unknown")]
            ))
        _, _, code, details = call_validate()
        wrong_algorithm_setting = experiment_spec[0].algorithm.algorithm_settings[0]
        self.assertEqual(code, grpc.StatusCode.INVALID_ARGUMENT)
        self.assertEqual(details,
                         "{name} {value} is not supported in Bayesian optimization".format(
                             name=wrong_algorithm_setting.name,
                             value=wrong_algorithm_setting.value
                         ))

        # wrong random_state
        experiment_spec[0] = api_pb2.ExperimentSpec(
            algorithm=api_pb2.AlgorithmSpec(
                algorithm_name="bayesianoptimization",
                algorithm_settings=[
                    api_pb2.AlgorithmSetting(name="random_state", value="-1")]
            ))
        _, _, code, details = call_validate()
        wrong_algorithm_setting = experiment_spec[0].algorithm.algorithm_settings[0]
        self.assertEqual(code, grpc.StatusCode.INVALID_ARGUMENT)
        self.assertEqual(details, "{name} should be great or equal than zero".format(name=wrong_algorithm_setting.name))


if __name__ == '__main__':
    unittest.main()
