import joblib
import pandas as pd
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


class LeadRandomForestRegressor:
    def __init__(self):
        print(BASE_DIR)
        path_to_artifacts = f'{BASE_DIR}' + '\\dump\\lead_regressor'
        self.values_fill_missing = joblib.load(
            path_to_artifacts + "\\train_mode.joblib")
        self.encoders = joblib.load(path_to_artifacts + "\\encoders.joblib")
        self.model = joblib.load(path_to_artifacts + "\\random_forest.joblib")

    def __str__(self):
        return f'LeadRandomForestRegressor'

    def __repr__(self):
        return f'LeadRandomForestRegressor'

    def preprocessing(self, input_data):
        # JSON to pandas DataFrame
        input_data = pd.DataFrame(input_data, index=[0])
        # fill missing values
        input_data.fillna(self.values_fill_missing)
        # convert categoricals
        for column in [
            'job_title', 'sex', 'email'
        ]:
            if column == 'sex' or column == 'email':
                categorical_convert = self.encoders[column]
                input_data[column] = categorical_convert.transform(
                    input_data[column])
            elif column == 'job_title':
                job_title_order = {'Director': 3, 'Manager': 2, 'Others': 1}
                categorical_convert = self.encoders[column]
                # categorical_convert.fit([['Director', 3], ['Manager', 2],
                #                         ['Others', 1]])
                input_data[column] = categorical_convert.transform(
                    [[job, job_title_order[job]] for job in input_data[column]])

        return input_data

    def predict(self, input_data):
        return self.model.predict(input_data)

    def postprocessing(self, input_data):
        # label = "Non-Promising"
        # if input_data[1] > 0.5:
        #     label = "Promising"
        return {"output": input_data, "label": 'label', "status": "OK"}

    def compute_prediction(self, input_data):
        try:
            input_data = self.preprocessing(input_data)
            prediction = self.predict(input_data)[0]  # only one sample
            prediction = self.postprocessing(prediction)
        except KeyError as ke:
            return {"status": "Key Error", "message": str(ke)}
        except Exception as e:
            return {"status": "Error", "message": str(e)}

        return prediction
