"""
WSGI config for salesfoo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""
import inspect
import os

from django.core.wsgi import get_wsgi_application

from apps.ml.income_classifier.random_forest import IncomeRandomForestClassifier
from apps.ml.lead_regressor.random_forest import LeadRandomForestRegressor
from apps.ml.registry import MLRegistry


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'salesfoo.settings')

application = get_wsgi_application()


# Ml Model Registry
try:
    registry = MLRegistry()
    # RF = IncomeRandomForestClassifier()
    # registry.add_algorithm(
    #     endpoint_name="income_classifier3",
    #     algorithm_object=RF,
    #     algorithm_name="random forest",
    #     algorithm_status="production",
    #     algorithm_version="0.0.1",
    #     owner="SalesFoo ML",
    #     algorithm_description="Random Forest with simple pre- and post-processing",
    #     algorithm_code=inspect.getsource(IncomeRandomForestClassifier)

    # )
    lrf = LeadRandomForestRegressor()
    registry.add_algorithm(
        endpoint_name="lead_score",
        algorithm_object=lrf,
        algorithm_name="lead random forest",
        algorithm_status="production",
        algorithm_version="0.0.2",
        owner="SalesFoo ML",
        algorithm_description="Random Forest with simple pre- and post-processing",
        algorithm_code=inspect.getsource(LeadRandomForestRegressor)
    )


except Exception as error:
    print(f'{error} : Exception While Laoding ML Model in Registry')
