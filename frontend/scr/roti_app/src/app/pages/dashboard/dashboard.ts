import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService, UserRole } from '../../services/auth.services';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.css']
})
export class DashboardComponent implements OnInit {
  usuario: any;
  rol: UserRole | null = null;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.usuario = this.authService.getCurrentUser();
    this.rol = this.authService.getUserRole();
  }

  logout() {
    this.authService.logout();
  }

  // Métodos para verificar roles
  isAdmin(): boolean {
    return this.rol === 'Administrador';
  }

  isEncargado(): boolean {
    return this.rol === 'Encargado';
  }

  isCliente(): boolean {
    return this.rol === 'Cliente';
  }
}