
import json
# from numpy.random import rand
from django.views import View
from django.http import JsonResponse
from rest_framework import viewsets, views, status, mixins
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from apps.ml.registry import MLRegistry
from apps.ml.lead_regressor.serializers import LeadSerializer
from salesfoo.wsgi import registry

from apps.initial.models import Endpoint
from apps.initial.serializers import EndpointSerializer

from apps.initial.models import MLAlgorithm
from apps.initial.serializers import MLAlgorithmSerializer

from apps.initial.models import MLAlgorithmStatus
from apps.initial.serializers import MLAlgorithmStatusSerializer

from apps.initial.models import MLRequest
from apps.initial.serializers import MLRequestSerializer

from rest_framework_api_key.permissions import HasAPIKey
import os


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


class PredictView(views.APIView):

    serializer_class = LeadSerializer
    permission_classes = [HasAPIKey]
    @swagger_auto_schema(request_body=LeadSerializer)
    def post(self, request, endpoint_name, format=None):

        algorithm_status = self.request.query_params.get(
            "status", "production")
        algorithm_version = self.request.query_params.get("version")

        algs = MLAlgorithm.objects.filter(
            parent_endpoint__name=endpoint_name, status__status=algorithm_status, status__active=True)

        if algorithm_version is not None:
            algs = algs.filter(version=algorithm_version)

        else:
            algs = algs.filter(version='0.0.2')

        if len(algs) == 0:
            return Response(
                {"status": "Error", "message": "ML algorithm is not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(algs) != 1 and algorithm_status != "ab_testing":
            print(algs)
            return Response(
                {"status": "Error", "message": "ML algorithm selection is ambiguous. Please specify algorithm version."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        alg_index = 0
        # if algorithm_status == "ab_testing":
        #     alg_index = 0 if rand() < 0.5 else 1
        input_features = request.data
        input_features["acquisition_channel=_Cold Call"] = request.data['acquisition_channel_Cold_Call']
        input_features["acquisition_channel=_Cold Email"] = request.data['acquisition_channel_Cold_Email']
        input_features["acquisition_channel=_Organic Search"] = request.data['acquisition_channel_Organic_Search']
        input_features["acquisition_channel=_Paid Leads"] = request.data['acquisition_channel_Paid_Leads']
        input_features["acquisition_channel=_Paid Search"] = request.data['acquisition_channel_Paid_Search']
        input_features["company_size=_1-10"] = request.data["company_size_1_to_10"]
        input_features["company_size=_11-50"] = request.data["company_size_11_to_50"]
        input_features["company_size=_51-100"] = request.data["company_size_51_to_100"]
        input_features["company_size=_101-250"] = request.data["company_size_101_to_250"]
        input_features["company_size=_251-1000"] = request.data["company_size_251_to_1000"]
        input_features["company_size=_1000-10000"] = request.data["company_size_1000_to_10000"]
        input_features["company_size=_10001+"] = request.data["company_size_10001_plus"]
        input_features["industry=_Financial Services"] = request.data["industry_Financial_Services"]
        input_features["industry=_Furniture"] = request.data["industry_Furniture"]
        input_features["industry=_Heavy Manufacturing"] = request.data["industry_Heavy_Manufacturing"]
        input_features["industry=_Scandanavion Design"] = request.data["industry_Scandanavion_Design"]
        input_features["industry=_Transportation"] = request.data["industry_Transportation"]
        input_features["industry=_Web & Internet"] = request.data["industry_Web_Internet"]

        to_pop = ["acquisition_channel_Cold_Call",
                  "acquisition_channel_Cold_Email",
                  "acquisition_channel_Organic_Search",
                  "acquisition_channel_Paid_Leads",
                  "acquisition_channel_Paid_Search",
                  "company_size_1_to_10",
                  "company_size_11_to_50",
                  "company_size_51_to_100",
                  "company_size_101_to_250",
                  "company_size_251_to_1000",
                  "company_size_1000_to_10000",
                  "company_size_10001_plus",
                  "industry_Financial_Services",
                  "industry_Furniture",
                  "industry_Heavy_Manufacturing",
                  "industry_Scandanavion_Design",
                  "industry_Transportation",
                  "industry_Web_Internet"]
        for key in to_pop:
            input_features.pop(key, None)

        algorithm_object = registry.endpoints[algs[alg_index].id]
        prediction = algorithm_object.compute_prediction(input_features)

        label = prediction["label"] if "label" in prediction else "error"

        ml_request = MLRequest(
            input_data=json.dumps(input_features),
            full_response=prediction,
            response=label,
            feedback="",
            parent_mlalgorithm=algs[alg_index],
        )
        ml_request.save()

        prediction["request_id"] = ml_request.id

        return Response(prediction)


class GetFeatureColumns(View):
    def get(self,  request):
        import joblib
        feature = joblib.load(
            PROJECT_DIR + './../dump/features_column.joblib')
        print(feature)
        return JsonResponse({'features': list(feature)})


class EndpointViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = EndpointSerializer
    queryset = Endpoint.objects.all()


class MLAlgorithmViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = MLAlgorithmSerializer
    queryset = MLAlgorithm.objects.all()


def deactivate_other_statuses(instance):
    old_statuses = MLAlgorithmStatus.objects.filter(parent_mlalgorithm=instance.parent_mlalgorithm,
                                                    created_at__lt=instance.created_at,
                                                    active=True)
    for i in range(len(old_statuses)):
        old_statuses[i].active = False
    MLAlgorithmStatus.objects.bulk_update(old_statuses, ["active"])


class MLAlgorithmStatusViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet,
    mixins.CreateModelMixin
):
    serializer_class = MLAlgorithmStatusSerializer
    queryset = MLAlgorithmStatus.objects.all()

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                instance = serializer.save(active=True)
                # set active=False for other statuses
                deactivate_other_statuses(instance)

        except Exception as e:
            raise APIException(str(e))


class MLRequestViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet,
    mixins.UpdateModelMixin
):
    serializer_class = MLRequestSerializer
    queryset = MLRequest.objects.all()
