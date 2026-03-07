from flask_restx import Namespace, Resource
from extensions import db
from models.research_request import ResearchRequest
from models.project import Project
from models.deployment import Deployment
from models.game import Game
from models.communication import Communication

api = Namespace("dashboard", description="Dashboard summary endpoints")

@api.route("/stats")
class DashboardStats(Resource):
    def get(self):
        new_requests = ResearchRequest.query.filter_by(status="submitted", soft_deleted=False).count()
        active_projects = Project.query.filter(Project.status.in_(["active","deployed"])).count()
        pending_approval = Project.query.filter_by(status="pending_approval").count()
        active_deployments = Deployment.query.filter_by(status="active").count()
        game_requests = Game.query.filter(Game.status.in_(["requirements_discussion","in_development"])).count()
        awaiting_response = Communication.query.filter_by(status="awaiting_admin").count()
        total_communications = Communication.query.count()

        # Weekly stub (frontend expects array)
        weekly = [
            {"day":"Mon","responses":145,"target":120},
            {"day":"Tue","responses":178,"target":120},
            {"day":"Wed","responses":203,"target":120},
            {"day":"Thu","responses":189,"target":120},
            {"day":"Fri","responses":234,"target":120},
            {"day":"Sat","responses":156,"target":120},
            {"day":"Sun","responses":142,"target":120}
        ]

        monthlyTrendData = [
            {"month":"Jul","projects":12,"deployments":8,"responses":1245},
            {"month":"Aug","projects":15,"deployments":12,"responses":1567},
            {"month":"Sep","projects":18,"deployments":15,"responses":1834},
            {"month":"Oct","projects":14,"deployments":11,"responses":1247}
        ]

        projectStatusData = [
            {"name":"Active","value":8,"color":"#3b82f6"},
            {"name":"Planning","value":5,"color":"#8b5cf6"},
            {"name":"Completed","value":12,"color":"#10b981"},
            {"name":"On Hold","value":2,"color":"#f59e0b"}
        ]

        locationPerformance = [
            {"location":"Walmart DT","responses":456,"completion":94},
            {"location":"Walmart NS","responses":389,"completion":91},
            {"location":"Target Loop","responses":312,"completion":88},
            {"location":"Walmart W","responses":90,"completion":45}
        ]

        return {
            "newRequests": new_requests,
            "activeProjects": active_projects,
            "pendingApproval": pending_approval,
            "activeDeployments": active_deployments,
            "gameRequests": game_requests,
            "awaitingResponse": awaiting_response,
            "totalCommunications": total_communications,
            "weeklyResponseData": weekly,
            "monthlyTrendData": monthlyTrendData,
            "projectStatusData": projectStatusData,
            "locationPerformance": locationPerformance
        }, 200
