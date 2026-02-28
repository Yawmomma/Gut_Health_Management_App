"""
Multi-User & Cohort Analysis Endpoints
For comparative analytics and cohort insights (experimental)
"""

from flask import jsonify
from . import bp
from utils.auth import require_api_key, require_scope


@bp.route('/users/cohort-analysis', methods=['GET'])
@require_api_key
@require_scope('admin:users')
def users_cohort_analysis():
    """
    Anonymous cohort analysis across users
    NOTE: This app is currently single-user. Multi-user support is experimental.
    """
    return jsonify({
        'status': 'single_user_mode',
        'message': 'Multi-user features are not enabled in single-user mode',
        'todo': 'Implement user account system and anonymous cohort data pooling'
    }), 200


@bp.route('/users/compare', methods=['GET'])
@require_api_key
@require_scope('admin:users')
def users_compare():
    """
    Compare user to similarity cluster
    NOTE: Requires multi-user mode
    """
    return jsonify({
        'status': 'single_user_mode',
        'message': 'Multi-user features are not enabled in single-user mode',
        'todo': 'Implement user cohort clustering and comparative metrics'
    }), 200


@bp.route('/users/phenotypes', methods=['GET'])
@require_api_key
@require_scope('admin:users')
def users_phenotypes():
    """
    Identify phenotype similarities with other users
    NOTE: Requires multi-user mode and advanced analytics
    """
    return jsonify({
        'status': 'single_user_mode',
        'message': 'Multi-user features are not enabled in single-user mode',
        'todo': 'Implement phenotype classification and similarity matching'
    }), 200
