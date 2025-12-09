"""
Interface Adapter: HTTP Handler
Implementa handlers HTTP para a aplicação
"""
import http.server
import json
from typing import Callable
from src.application.services.health_check_service import HealthCheckService
from src.application.services.user_service import UserService


class HTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Handler HTTP que processa requisições e delega para serviços"""

    health_check_service: HealthCheckService = None
    user_service: UserService = None

    def do_GET(self):
        """Processa requisições GET"""
        if self.path == '/':
            self._handle_root()
        elif self.path == '/health':
            self._handle_health_check()
        elif self.path.startswith('/users'):
            self._handle_get_users()
        else:
            self._send_error_response(404, "Not Found")

    def _handle_root(self):
        """Handler para rota raiz"""
        self._send_json_response(200, {
            "status": "CreditAI API2"
        })

    def _handle_health_check(self):
        """Handler para health check"""
        if not self.health_check_service:
            self._send_error_response(500, "Health check service not configured")
            return

        health_status = self.health_check_service.get_health_status()
        status_code = 200 if health_status.is_healthy else 503

        self._send_json_response(status_code, {
            "status": health_status.status,
            "services": health_status.services
        })

    def _handle_get_users(self):
        """Handler para listar usuários"""
        if not self.user_service:
            self._send_error_response(500, "User service not configured")
            return

        try:
            users = self.user_service.get_all_users()
            users_data = [
                {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ]
            self._send_json_response(200, {"users": users_data, "count": len(users_data)})
        except Exception as e:
            self._send_error_response(500, f"Error fetching users: {str(e)}")

    def _send_json_response(self, status_code: int, data: dict):
        """Envia uma resposta JSON"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _send_error_response(self, status_code: int, message: str):
        """Envia uma resposta de erro"""
        self._send_json_response(status_code, {"error": message})

    def log_message(self, format, *args):
        """Override para customizar logs"""
        print(f"[{self.log_date_time_string()}] {format % args}")
