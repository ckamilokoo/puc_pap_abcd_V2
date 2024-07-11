#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2024.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

import inspect
import os
import re
from typing import Callable, Any

from ibm_watsonx_ai.client import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.extensions.rag import VectorStore
from ibm_watsonx_ai.foundation_models.extensions.rag.pattern.default_deployable_function import (
    default_deployable_function,
)
from ibm_watsonx_ai.foundation_models.prompts import PromptTemplateManager
from ibm_watsonx_ai.foundation_models.utils.enums import PromptTemplateFormats
from ibm_watsonx_ai.metanames import RAGPatternParamsMetaNames
from ibm_watsonx_ai.wml_client_error import (
    InvalidMultipleArguments,
    InvalidValue,
    MissingValue,
    ValidationError,
    WMLClientError,
)


DEFAULT_RAG_PARAMS = {
    RAGPatternParamsMetaNames.NUM_RETRIEVED_DOCS: 3,
}


class RAGPattern:
    """Class for defining, querying and deploying Retrieval-Augmented Generation (RAG) patterns."""

    def __init__(
        self,
        *,
        space_id: str,
        api_client: APIClient | None = None,
        auto_store: bool | None = False,
        credentials: Credentials | dict | None = None,
        model: ModelInference | None = None,
        prompt_id: str | None = None,
        python_function: Callable | None = None,
        rag_params: dict | None = None,
        store_params: dict | None = None,
        vector_store: VectorStore | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the ``RAGPattern`` object.

        .. note::
            If the pattern's components (``vector_store``, ``prompt_id``, ``model``) are specified, the pattern will use default function template for querying and deployment.
            If custom ``python_function`` is specfied, the pattern's components are not utilized.

        .. hint::
            Both default function template and custom ``python_function`` provided by user can by modified by changing :meth:`pretty_print`'s output.

        :param space_id: ID of the Watson Studio space
        :type space_id: str

        :param api_client: initialized APIClient object, defaults to None
        :type api_client: APIClient, optional

        :param auto_store: whether to store the ``python_function`` in the repository upon initialization, defaults to False
        :type auto_store: bool, optional

        :param credentials: credentials to Watson Machine Learning instance, defaults to None
        :type credentials: ibm_watsonx_ai.Credentials or dict, optional

        :param model: initialized :class:`ModelInference <ibm_watsonx_ai.foundation_models.inference.model_inference.ModelInference>` object, defaults to None
        :type model: ModelInference, optional

        :param prompt_id: Initialized ID of :class:`PromptTemplate <ibm_watsonx_ai.foundation_models.prompts.prompt_template.PromptTemplate>` object stored in space.
            Required to have ``{question}`` and ``{reference_documents}`` input variables when used with default python function, defaults to None
        :type prompt_id: str, optional

        :param python_function: custom python function generator containing RAG logic, defaults to None
        :type python_function: Callable, optional

        :param rag_params: optional parameters passed to the python function, to see available meta names use: ``RAGPatternParamsMetaNames().show()`` , defaults to None
        :type rag_params: dict, optional

        :param store_params: properites used for storing function in the repository, to see available meta names use: ``client.repository.FunctionMetaNames.show()``, defaults to None
        :type store_params: dict, optional

        :param vector_store: initialized :class:`VectorStore <ibm_watsonx_ai.foundation_models.extensions.rag.vector_stores.vector_store.VectorStore>` object, defaults to None
        :type vector_store: VectorStore, optional

        .. note::
            For ``python_function`` to be populated with parameters passed at initialization the function's signature must have a default parameter called ``params`` as its last parameter.

            .. code-block:: python

                def custom_python_function(custom_arg='value', params=None):
                    def score(payload):
                        return payload
                    return score


        **Example**

        .. code-block:: python

            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models.extensions.rag import RAGPattern

            def custom_python_function(custom_arg='value', params=None):
                def score(payload):
                    return payload
                return score

            pattern = RAGPattern(
                space_id="<ID of the space>",
                python_function=custom_python_function,
                credentials=Credentials(
                                api_key = "***",
                                url = "https://us-south.ml.cloud.ibm.com")
            )

        .. code-block:: python

            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference
            from ibm_watsonx_ai.foundation_models.extensions.rag import RAGPattern, VectorStore

            vector_store = VectorStore(...)
            model = ModelInference(...)

            pattern = RAGPattern(
                space_id="<ID of the space>",
                vector_store=vector_store,
                prompt_id="<ID of the prompt template>",
                model=model,
                credentials=Credentials(
                            api_key = "***",
                            url = "https://us-south.ml.cloud.ibm.com")
            )

        """
        self.space_id = space_id
        self.model = model
        self.prompt_id = prompt_id
        self.rag_params = DEFAULT_RAG_PARAMS
        self.store_params = store_params
        self.vector_store = vector_store
        self.kwargs = kwargs

        self.deployment_id: str | None = None
        self.function_id = None
        self.prompt_text = None
        self._stored = False
        self._deployed = False

        self._validate_kwargs()

        if api_client is not None:
            self._credentials = api_client.credentials
        elif credentials is not None:
            if isinstance(credentials, dict):
                credentials = Credentials.from_dict(credentials)
            self._credentials = credentials
        else:
            raise InvalidMultipleArguments(
                params_names_list=["credentials", "api_client"],
                reason="None of the arguments were provided.",
            )

        self._credentials.verify = True
        self._client = APIClient(self._credentials)
        self._client.set.default_space(space_id)

        if rag_params:
            self.rag_params.update(rag_params)

        if python_function:
            self.python_function = self._populate_default_params(python_function)

            if auto_store:
                if (
                    not store_params
                    or self._client.repository.FunctionMetaNames.NAME
                    not in store_params
                ):
                    name = python_function.__name__
                else:
                    name = store_params.get(  # type: ignore[assignment]
                        self._client.repository.FunctionMetaNames.NAME
                    )

                function_details = self._store_function(
                    name=name,
                    python_function=python_function,
                    store_params=store_params,
                )
                self.function_id = self._client.repository.get_function_id(
                    function_details
                )
        else:
            if not vector_store:
                raise MissingValue(
                    value_name="vector_store",
                    reason="VectorStore object must be provided when python function is not provided.",
                )

            if prompt_id:
                self.prompt_text = self._load_prompt_text(prompt_id)
            elif prompt_text := kwargs.get("prompt_text"):
                self._validate_prompt_text(prompt_text)
                self.prompt_text = prompt_text
            else:
                raise MissingValue(
                    value_name="prompt_id",
                    reason="Prompt ID must be provided when python function is not provided.",
                )

            if not model:
                raise MissingValue(
                    value_name="model",
                    reason="ModelInference object must be provided when python function is not provided.",
                )

            self.python_function = self._populate_default_params(
                default_deployable_function
            )

    def deploy(
        self,
        name: str,
        store_params: dict | None = None,
        deploy_params: dict | None = None,
    ) -> dict:
        """Store and deploy ``python_function`` to the space.

        .. hint::
            If custom software specification is not specified in ``store_params``, RAGPattern will automatically create and use one.

        :param name: Name for the stored function object as well as the deployed function. Can be overwritten by ``store_params`` and ``deploy_params``.
        :type name: str

        :param store_params: properites used for storing function in the repository, to see available meta names use: ``client.repository.FunctionMetaNames.show()``, defaults to None
        :type store_params: dict, optional

        :param deploy_params: properites used for deploying function to the space, to see available meta names use: ``client.deployments.ConfigurationMetaNames.show()``, defaults to None
        :type deploy_params: dict, optional

        :return: details of the deployed python function
        :rtype: dict

        **Example**

        .. code-block:: python

            pattern.deploy(name="Example deployment name")

        .. code-block:: python

            deployment_details = pattern.deploy(
                name="Example deployment name",
                store_params={"software_spec_id": "<ID of the custom sw spec>"},
                deploy_params={"description": "Optional deployed function description"}
            )

        """
        store_params = store_params or self.store_params

        if not self._stored:
            function_details = self._store_function(
                name=name,
                python_function=self.python_function,
                store_params=store_params,
            )
            self.function_id = self._client.repository.get_function_id(function_details)

        deployment_details = self._deploy_function(
            name=name, python_function_id=self.function_id, deploy_params=deploy_params  # type: ignore[arg-type]
        )
        self.deployment_id = self._client.deployments.get_id(deployment_details)

        return deployment_details

    def query(self, payload: dict) -> dict:
        """Query the python function locally, without deploying.

        :param payload: payload for the scoring function
        :type payload: dict

        :return: result of the scorig function
        :rtype: dict

        **Example**

        .. code-block:: python

            payload = {
                client.deployments.ScoringMetaNames.INPUT_DATA: [{
                    "fields": ["Text"],
                    "values": ["When was IBM founded?"]
                }]
            }
            result = pattern.query(payload)

        """
        return self.python_function()(payload)

    def pretty_print(self, insert_to_cell: bool = False) -> None:
        """Print the python function's source code to ispect or modify.

        :param insert_to_cell: whether to insert python function's source code to a new notebook cell, defaults to False
        :type insert_to_cell: bool, optional
        """
        code = inspect.getsource(self.python_function)
        args_spec = inspect.getfullargspec(self.python_function)

        defaults: tuple | list = args_spec.defaults or []
        args = args_spec.args or []

        args_pattern = ",".join([rf"\s*{arg}\s*=\s*(.+)\s*" for arg in args])
        pattern = rf"^def {self.python_function.__name__}\s*\({args_pattern}\)\s*:"
        res = re.match(pattern, code)

        for i in range(len(defaults) - 1, -1, -1):
            default = defaults[i]
            if isinstance(default, dict):
                default = {
                    key: val for key, val in default.items() if "credentials" not in key
                }
            code = (
                code[: res.start(i + 1)] + default.__repr__() + code[res.end(i + 1) :]  # type: ignore[union-attr]
            )

        if insert_to_cell:
            from IPython.core.getipython import get_ipython

            ipython = get_ipython()
            comment = "# generated by RAGPattern.pretty_print\n# credentials have been redacted\n\n"
            ipython.set_next_input(comment + code, replace=False)
        else:
            print(code)

    def delete(self, delete_stored_function: bool = True) -> None:
        """Delete stored function object and/or deployed function from space.

        :param delete_stored_function: whether to delete stored function object from the repository, defaults to True
        :type delete_stored_function: bool, optional
        """
        if self._deployed:
            try:
                self._client.deployments.delete(self.deployment_id)
                self.deployment_id = None
                self._deployed = False
            except WMLClientError as e:
                raise WMLClientError(
                    f"Could not delete deployment with ID: '{self.deployment_id}'"
                ) from e

        if delete_stored_function and self._stored:
            try:
                self._client.repository.delete(self.function_id)
                self.function_id = None
                self._stored = False
            except WMLClientError as e:
                raise WMLClientError(
                    f"Could not delete function with ID: '{self.function_id}'"
                ) from e

    def _validate_kwargs(self) -> None:
        """Check if all passed keyword arguments are supported.

        :raises InvalidValue: if any keyword argument is not supported
        """
        SUPPORTED_KWARGS = ["prompt_text"]

        for kwarg in self.kwargs.keys():
            if kwarg not in SUPPORTED_KWARGS:
                raise InvalidValue(
                    kwarg,
                    reason=f"{kwarg} is not supported as a keyword argument. Supported kwargs: {SUPPORTED_KWARGS}",
                )

    def _validate_prompt_text(self, prompt_text: str) -> None:
        """Check if prompt text has required input variables."

        :param prompt_text: prompt as text with placeholders
        :type prompt_text: str

        :raises ValidationError: if any required input variable missing
        """
        REQUIRED_INPUT_VARIABLES = ["{question}", "{reference_documents}"]

        for key in REQUIRED_INPUT_VARIABLES:
            if key not in prompt_text:
                raise ValidationError(key)

    def _load_prompt_text(self, prompt_id: str) -> str:
        """Load prompt as string and validate input variables.
        ``REQUIRED_INPUT_VARIABLES`` are expected by the default deployable function.

        :param prompt_id: ID of :class:`PromptTemplate <ibm_watsonx_ai.foundation_models.prompts.prompt_template.PromptTemplate>` stored in space
        :type prompt_id: str

        :return: prompt with placeholders as string
        :rtype: str
        """
        prompt_mgr = PromptTemplateManager(api_client=self._client)
        prompt_text = prompt_mgr.load_prompt(prompt_id, PromptTemplateFormats.STRING)

        self._validate_prompt_text(prompt_text)

        return prompt_text

    def _populate_default_params(self, function: Callable) -> Callable:
        """Populate python function's default params by updating and overwritting.
        Default parameter named ``params`` is used to pass information that is used inside deployed function.
        Can be used both with default function template and custom function (if signature matches).

        :param function: function which default params should be populated
        :type function: Callable

        :return: function with params populated if signature matches
        :rtype: Callable
        """
        args_spec = inspect.getfullargspec(function)
        defaults: tuple | list = args_spec.defaults or []
        args = args_spec.args or []

        if len(args) > 0 and args[-1] == "params":
            default_deployable_params = {
                "credentials": self._credentials.to_dict(),
                "space_id": self.space_id,
                "vector_store": (
                    self.vector_store.to_dict() if self.vector_store else None
                ),
                "prompt": self.prompt_text,
                "model": self.model.get_identifying_params() if self.model else None,
                "rag_params": self.rag_params,
            }

            if provided_deployable_params := defaults[-1]:
                default_deployable_params.update(provided_deployable_params)
            function.__defaults__ = (*defaults[:-1], default_deployable_params)

        return function

    def _create_custom_software_spec(self) -> dict:
        """Create a custom software specification for pattern deployment.

        :return: details of the custom software specification
        :rtype: dict
        """
        BASE_SW_SPEC_NAME = "runtime-23.1-py3.10"
        SW_SPEC_NAME = "rag_23.1-py3.10"
        PKG_EXTN_NAME = "rag_pattern-py3.10"
        CONFIG_PATH = "config.yaml"
        CONFIG_TYPE = "conda_yml"
        CONFIG_CONTENT = """
        name: python310
        channels:
          - empty
        dependencies:
          - pip:
            - elasticsearch
            - gensim
            - langchain
            - pydantic
            - sentence-transformers
        prefix: /opt/anaconda3/envs/python310
        """

        sw_spec_id = self._client.software_specifications.get_id_by_name(SW_SPEC_NAME)
        if sw_spec_id != "Not Found":
            return self._client.software_specifications.get_details(sw_spec_id)

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(CONFIG_CONTENT)

        try:
            pkg_extn_meta_props = {
                self._client.package_extensions.ConfigurationMetaNames.NAME: PKG_EXTN_NAME,
                self._client.package_extensions.ConfigurationMetaNames.TYPE: CONFIG_TYPE,
            }

            pkg_extn_details = self._client.package_extensions.store(
                meta_props=pkg_extn_meta_props, file_path=CONFIG_PATH
            )
            pkg_extn_uid = self._client.package_extensions.get_id(pkg_extn_details)

            sw_spec_meta_props = {
                self._client.software_specifications.ConfigurationMetaNames.NAME: SW_SPEC_NAME,
                self._client.software_specifications.ConfigurationMetaNames.BASE_SOFTWARE_SPECIFICATION: {
                    "guid": self._client.software_specifications.get_id_by_name(
                        BASE_SW_SPEC_NAME
                    )
                },
            }

            sw_spec_details = self._client.software_specifications.store(
                meta_props=sw_spec_meta_props
            )
            sw_spec_id = self._client.software_specifications.get_id(sw_spec_details)

            self._client.software_specifications.add_package_extension(
                sw_spec_id, pkg_extn_uid
            )
        finally:
            os.remove(CONFIG_PATH)

        return self._client.software_specifications.get_details(sw_spec_id)

    def _store_function(
        self, name: str, python_function: Callable, store_params: dict | None = None
    ) -> dict:
        """Store the ``python_function`` in the repository.

        :param name: name of the stored python function object
        :type name: str

        :param python_function: the function to be stored
        :type python_function: Callable

        :param store_params: properites used for storing the function object, defaults to None
        :type store_params: dict, optional

        :return: details of the stored function
        :rtype: dict
        """
        if (
            not store_params
            or self._client.repository.FunctionMetaNames.SOFTWARE_SPEC_ID
            not in store_params
        ):
            custom_sw_spec_details = self._create_custom_software_spec()
            software_spec_id = self._client.software_specifications.get_id(
                custom_sw_spec_details
            )
        else:
            software_spec_id = store_params[
                self._client.repository.FunctionMetaNames.SOFTWARE_SPEC_ID
            ]

        meta_props = {
            self._client.repository.FunctionMetaNames.NAME: name,
            self._client.repository.FunctionMetaNames.SOFTWARE_SPEC_ID: software_spec_id,
        }

        if store_params:
            meta_props.update(store_params)

        function_details = self._client.repository.store_function(
            function=python_function, meta_props=meta_props
        )
        self._stored = True

        return function_details

    def _deploy_function(
        self, name: str, python_function_id: str, deploy_params: dict | None = None
    ) -> dict:
        """Deploy function object with ``python_function_id`` to space.

        :param name: name of the deployed python function
        :type name: str

        :param python_function_id: ID of the function object
        :type python_function_id: str

        :param deploy_params: properites used for deploying the function object, to see available meta names use: ``client.deployments.ConfigurationMetaNames.show()``, defaults to None
        :type deploy_params: dict, optional

        :return: details of the deployed function
        :rtype: dict | None
        """
        meta_props = {
            self._client.deployments.ConfigurationMetaNames.NAME: name,
            self._client.deployments.ConfigurationMetaNames.ONLINE: {},
        }

        if deploy_params:
            meta_props.update(deploy_params)

        deployment_details = self._client.deployments.create(
            artifact_id=python_function_id, meta_props=meta_props
        )
        self._deployed = True

        return deployment_details
