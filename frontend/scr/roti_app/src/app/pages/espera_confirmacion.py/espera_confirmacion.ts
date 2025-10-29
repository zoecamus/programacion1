import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.services';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-espera-confirmacion',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './espera_confirmacion.html',
  styleUrls: ['./espera_confirmacion.css']
})
export class EsperaConfirmacionComponent implements OnInit {
  usuarioEmail: string = '';
  verificandoEstado: boolean = false;

  constructor(
    private authService: AuthService,
    private router: Router,
    private http: HttpClient
  ) {}

  ngOnInit() {
    const user = this.authService.getCurrentUser();
    if (!user) {
      // Si no hay usuario, redirigir al login
      this.router.navigate(['/login']);
      return;
    }
    
    this.usuarioEmail = user.email || '';
    
    // Verificar estado cada 10 segundos
    this.verificarEstadoPeriodicamente();
  }

  verificarEstadoPeriodicamente() {
    setInterval(() => {
      this.verificarEstado();
    }, 10000); // Cada 10 segundos
  }

  verificarEstado() {
    this.verificandoEstado = true;
    const token = this.authService.getToken();
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.get<any>(`http://localhost:7000/user/${this.usuarioEmail}`, { headers }).subscribe({
      next: (response) => {
        console.log('Estado del usuario:', response);
        
        if (response.estado === 'Activo') {
          // Usuario aprobado, redirigir al menú
          alert('¡Tu cuenta ha sido aprobada! Ya puedes realizar pedidos.');
          this.router.navigate(['/productos']);
        } else if (response.estado === 'Rechazado') {
          // Usuario rechazado
          alert('Tu solicitud de cuenta fue rechazada. Contacta al administrador.');
          this.authService.logout();
        }
        
        this.verificandoEstado = false;
      },
      error: (err) => {
        console.error('Error al verificar estado:', err);
        this.verificandoEstado = false;
      }
    });
  }

  verificarAhora() {
    this.verificarEstado();
  }

  cerrarSesion() {
    if (confirm('¿Cerrar sesión?')) {
      this.authService.logout();
    }
  }
}