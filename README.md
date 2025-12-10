# Data Collection and Description
2-1.py - Web scraping script for collecting car listing URLs from Otomoto.pl. Uses BeautifulSoup to extract car listing URLs from search result pages with progress tracking and error handling.
2-2.py - URL deduplication utility that removes duplicate car listing URLs from the scraped data. Reads from otomoto_car_urls.txt and outputs unique URLs to otomoto_car_urls_unique.txt.
2-3.py - Car details scraper that extracts detailed information from individual car listing pages. Processes URLs from the unique list and extracts JSON data containing car specifications, prices, and features with progress tracking.
2-4.py - Data preprocessing and cleaning pipeline that processes the raw scraped car data. Converts JSON data to structured format, handles currency conversion (EUR to PLN), filters for undamaged used vehicles, concatenates text fields, and prepares data for modeling.
2-5.ipynb - Initial data exploration and preprocessing notebook. Analyzes the parsed car data, converts boolean columns, and prepares the dataset for feature engineering.
2-6.ipynb - Feature engineering and text processing notebook. Creates embeddings from car descriptions, generates PCA components, and prepares multiple datasets for different modeling approaches.
2-7.ipynb - Data preparation and cross-validation setup notebook. Creates train/test splits and prepares datasets for LinearRegression, DecisionTree, and BART models.
2-8.ipynb - Advanced feature engineering and dataset creation notebook. Generates final modeling datasets with proper cross-validation folds and feature transformations.

# Machine Learning Models Training and Evaluation
3-1.ipynb - Linear regression modeling notebook. Implements LinearRegression, Ridge, and Lasso models with cross-validation and hyperparameter tuning for car price prediction.
3-2.ipynb - Decision tree and ensemble modeling notebook. Implements DecisionTree, RandomForest, and GradientBoosting models with cross-validation and feature importance analysis.
3-3.ipynb - Neural network modeling notebook. Implements MLP (Multi-Layer Perceptron) models with PyTorch, including cross-validation, early stopping, and performance evaluation.
3-4.ipynb - TabNet implementation notebook. Implements TabNet deep learning model for tabular data with attention mechanisms and feature selection capabilities.
3-5.ipynb - TabTransformer implementation notebook. Implements transformer-based models for tabular data using the rtdl library, including cross-validation and performance evaluation.
3-6.ipynb - Early fusion neural network notebook. Implements early fusion architecture that combines structural features and text embeddings in a unified neural network model.
3-7.ipynb - Late fusion modeling notebook. Implements late fusion approaches that combine predictions from multiple models (structural and text-based) for improved performance.
3-8.ipynb - BART (Bayesian Additive Regression Trees) modeling notebook. Implements BART models for car price prediction with Bayesian inference and uncertainty quantification.
3-9.ipynb - Model comparison and ensemble methods notebook. Compares performance across all implemented models and creates ensemble predictions.
3-10.ipynb - Advanced model evaluation and interpretation notebook. Provides detailed analysis of model performance, feature importance, and prediction explanations.
3-11.ipynb - Final results and visualization notebook. Creates comprehensive visualizations, performance summaries, and final model selection for the car price prediction project. 