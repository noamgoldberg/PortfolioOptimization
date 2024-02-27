from typing import Optional, Literal
from sklearn.model_selection import cross_val_score as sk_cross_val_score, TimeSeriesSplit, KFold
from sklearn.base import BaseEstimator
import numpy as np

def cross_val_score(model: BaseEstimator, X: np.ndarray, y: np.ndarray, 
                    cross_val: Optional[Literal["standard", "time_series"]] = "standard", 
                    n_splits: int = 5) -> float:
    """
    Evaluates a model using cross-validation, with support for time series data.
    
    Parameters:
    - model: The machine learning model to be evaluated.
    - X: Feature dataset.
    - y: Target variable.
    - cross_val: Type of cross-validation. "standard" for regular cross-validation,
                 "time_series" for time series cross-validation to prevent data leakage.
    - n_splits: Number of cross-validation splits/folds.
    
    Returns:
    - The average cross-validation score.
    """
    if cross_val == "time_series":
        cv = TimeSeriesSplit(n_splits=n_splits)
    else:  # Default to standard K-Fold cross-validation
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    # Compute cross-validation scores
    scores = sk_cross_val_score(model, X, y, cv=cv)
    
    # Return the average score across all folds
    return np.mean(scores)