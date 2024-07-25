from flask import Blueprint, request, jsonify
from app.models import db, Incident, Resolution
from app.incident_handler import handle_incident

main = Blueprint('main', __name__)

@main.route('/api/incidents', methods=['POST'])
def create_incident():
    data = request.json
    new_incident = Incident(
        customer_id=data['customer_id'],
        description=data['description'],
        priority=data.get('priority', 'Low')
    )
    db.session.add(new_incident)
    db.session.commit()
    
    # Trigger automated handling
    handle_incident(new_incident)
    
    return jsonify({'message': 'Incident created', 'id': new_incident.id}), 201

@main.route('/api/incidents', methods=['GET'])
def get_incidents():
    incidents = Incident.query.all()
    return jsonify([
        {
            'id': i.id,
            'customer_id': i.customer_id,
            'description': i.description,
            'status': i.status,
            'priority': i.priority,
            'created_at': i.created_at.isoformat()
        } for i in incidents
    ])

@main.route('/api/incidents/<int:incident_id>', methods=['GET'])
def get_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    return jsonify({
        'id': incident.id,
        'customer_id': incident.customer_id,
        'description': incident.description,
        'status': incident.status,
        'priority': incident.priority,
        'created_at': incident.created_at.isoformat(),
        'resolutions': [
            {
                'id': r.id,
                'resolution_text': r.resolution_text,
                'resolved_at': r.resolved_at.isoformat()
            } for r in incident.resolutions
        ]
    })

@main.route('/api/incidents/<int:incident_id>/resolve', methods=['POST'])
def resolve_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    data = request.json
    resolution = Resolution(
        incident_id=incident.id,
        resolution_text=data['resolution_text']
    )
    incident.status = 'Resolved'
    db.session.add(resolution)
    db.session.commit()
    return jsonify({'message': 'Incident resolved'}), 200