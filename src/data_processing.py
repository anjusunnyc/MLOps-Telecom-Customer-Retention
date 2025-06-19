# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 22:10:53 2025

@author: Admin
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
from config.paths_config import *
from utils.common_functions import read_yaml
from src.logger import get_logger
from src.custom_exception import CustomException

logger = get_logger(__name__)

class ChurnDataProcessor:
    def __init__(self, config_path):
        
        self.config = read_yaml(config_path)
        self.raw_data_path = self.config["data_ingestion"]["raw_data_path"]
        self.processed_dir = PROCESSED_DIR  # from paths_config
        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

    def load_data(self):
        try:
            logger.info("Loading raw churn data")
            df = pd.read_csv(self.raw_data_path)
            # Coerce TotalCharges to numeric
            df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors='coerce')

            # Convert SeniorCitizen to categorical 'Yes'/'No'
            df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"}).astype("category")
            return df
        except Exception as e:
            raise CustomException("Error loading data", e)

    def label_encode_target(self, df, target_col='Churn'):
        logger.info("Encoding target variable: Yes/No → 1/0")
        df[target_col] = df[target_col].map({'Yes': 1, 'No': 0})
        return df
    def split_data(self, df):
        logger.info("Splitting data into train, validation, test sets")
        test_ratio = self.config['data_ingestion']['test_size']
        val_ratio = self.config['data_ingestion']['val_size']

        X = df.drop(columns=['Churn','customerID'])
        y = df['Churn']

        X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=test_ratio, random_state=42)
        val_relative_size = val_ratio / (1 - test_ratio)
        X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=val_relative_size, random_state=42)

        return X_train, X_val, X_test, y_train, y_val, y_test
    
    
    
    def impute_missing_values(self, X_train, X_val, X_test):
         logger.info("Imputing missing values")

         num_cols = self.config['data_processing']['numerical_columns']

         # Numerical imputer
         num_imputer = SimpleImputer(strategy='median')
         X_train[num_cols] = num_imputer.fit_transform(X_train[num_cols])
         X_val[num_cols] = num_imputer.transform(X_val[num_cols])
         X_test[num_cols] = num_imputer.transform(X_test[num_cols])

         

         return X_train, X_val, X_test


    def encode_categorical_columns(self, X_train, X_val, X_test):
        logger.info("Label encoding categorical columns")

        cat_cols = self.config['data_processing']['categorical_columns']
        encoders = {}

        for col in cat_cols:
            le = LabelEncoder()
            X_train[col] = le.fit_transform(X_train[col].astype(str))
            X_val[col] = le.transform(X_val[col].astype(str))
            X_test[col] = le.transform(X_test[col].astype(str))
            encoders[col] = le
            logger.info(f"{col} mapping: {dict(zip(le.classes_, le.transform(le.classes_)))}")

        return X_train, X_val, X_test
    def apply_smote(self, X_train, y_train):
        try:
            logger.info("Applying SMOTE to balance the training set")
            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

            logger.info(f"After SMOTE - Class distribution: {dict(pd.Series(y_resampled).value_counts())}")
            return X_resampled, y_resampled

        except Exception as e:
              logger.error(f"Error applying SMOTE: {e}")
              raise CustomException("SMOTE application failed", e)
    def save_dataframe(self, df, path):
      try:
        df.to_csv(path, index=False)
        logger.info(f"Saved processed data to: {path}")
      except Exception as e:
        logger.error(f"Failed to save data to {path}: {e}")
        raise CustomException("Saving data failed", e)
    
    def process(self):
        try:
            df = self.load_data()
            df = self.label_encode_target(df)
            X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(df)
            X_train, X_val, X_test = self.impute_missing_values(X_train, X_val, X_test)
            X_train, X_val, X_test = self.encode_categorical_columns(X_train, X_val, X_test)
            X_train, y_train = self.apply_smote(X_train, y_train)
            train_df = pd.concat([X_train, y_train.reset_index(drop=True)], axis=1)
            val_df = pd.concat([X_val, y_val.reset_index(drop=True)], axis=1)
            test_df = pd.concat([X_test, y_test.reset_index(drop=True)], axis=1)

            self.save_dataframe(train_df, os.path.join(self.processed_dir, "train.csv"))
            self.save_dataframe(val_df, os.path.join(self.processed_dir, "val.csv"))
            self.save_dataframe(test_df, os.path.join(self.processed_dir, "test.csv"))

            logger.info("Churn data preprocessing completed successfully.")

        except Exception as e:
            logger.error(f"Error during preprocessing: {e}")
            raise CustomException("Preprocessing failed", e)


if __name__ == "__main__":
    processor = ChurnDataProcessor(
        config_path=CONFIG_PATH
    )
    processor.process()
