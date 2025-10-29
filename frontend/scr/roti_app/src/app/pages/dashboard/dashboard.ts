import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, RouterOutlet } from '@angular/router';
import { AuthService } from '../../services/auth.services';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterOutlet],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css']
})
export class DashboardComponent implements OnInit {
  rol: string | null = null;
  usuario: any = null;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.rol = this.authService.getUserRole();
    this.usuario = this.authService.getCurrentUser();

    if (!this.rol) {
      // Si no hay usuario logueado, lo manda al login
      this.router.navigate(['/login']);
      return;
    }

    // NO redirigimos automáticamente, dejamos que el dashboard se muestre
    // El usuario puede navegar desde las cards
  }

  logout() {
    this.authService.logout();
  }

  isAdmin(): boolean {
    return this.rol === 'Administrador';
  }

  isEmpleado(): boolean {
    return this.rol === 'Empleado';
  }

  isEncargado(): boolean {
    return this.rol === 'Encargado';
  }

  isCliente(): boolean {
    return this.rol === 'Cliente';
  }
}