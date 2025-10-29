import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService, UserRole } from '../../services/auth.services';
import { Router } from '@angular/router';

interface Usuario {
  id: string;
  nombre: string;
  apellido: string;
  email: string;
  rol: string;
  telefono: string;
  estado?: string;
}

@Component({
  selector: 'app-usuarios',
  standalone: true,
  templateUrl: './usuarios.html',
  styleUrls: ['./usuarios.css'],
  imports: [CommonModule, FormsModule]
})
export class UsuariosComponent implements OnInit {
  usuarios: Usuario[] = [];
  busqueda: string = '';
  currentUserRole: UserRole | null = null;
  loading: boolean = true;
  error: string = '';

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.currentUserRole = this.authService.getUserRole();
    this.cargarUsuarios();
  }

  // ========== PERMISOS ==========
  
  // Solo Admin puede cambiar roles
  esAdmin(): boolean {
    return this.currentUserRole === 'Administrador';
  }

  // Admin puede cambiar roles, Encargado NO
  puedeCambiarRol(): boolean {
    return this.currentUserRole === 'Administrador';
  }

  // Admin y Encargado pueden gestionar usuarios (aprobar, bloquear)
  puedeGestionarUsuarios(): boolean {
    return this.currentUserRole === 'Administrador' || 
           this.currentUserRole === 'Encargado';
  }

  // Admin y Encargado pueden cambiar estado (Activo, Bloqueado, Pendiente)
  puedeEditarEstado(): boolean {
    return this.currentUserRole === 'Administrador' || 
           this.currentUserRole === 'Encargado';
  }

  // Solo Admin puede eliminar usuarios
  puedeEliminar(): boolean {
    return this.currentUserRole === 'Administrador';
  }

  cargarUsuarios() {
    const token = this.authService.getToken();
    
    if (!token) {
      this.error = 'No hay token. Inicia sesión de nuevo.';
      this.loading = false;
      return;
    }

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    this.http.get<any>('http://localhost:7000/users', { headers }).subscribe({
      next: (response) => {
        this.usuarios = response.usuarios || [];
        this.loading = false;
      },
      error: (err) => {
        console.error('Error:', err);
        this.error = 'Error al cargar usuarios';
        this.loading = false;
      }
    });
  }

  get usuariosFiltrados(): Usuario[] {
    return this.usuarios.filter(u =>
      u.nombre.toLowerCase().includes(this.busqueda.toLowerCase()) ||
      u.email.toLowerCase().includes(this.busqueda.toLowerCase())
    );
  }

  getRolBadgeClass(rol: string): string {
    if (rol === 'Administrador') return 'text-bg-danger';
    if (rol === 'Encargado') return 'text-bg-info';
    return 'text-bg-primary';
  }

  volverDashboard() {
    this.router.navigate([this.authService.getRedirectUrl()]);
  }

  aprobarUsuario(id: string) {
    if (confirm('¿Aprobar este usuario?')) {
      this.cambiarEstado(id, 'Activo');
    }
  }
  
  rechazarUsuario(id: string) {
    if (confirm('¿Rechazar este usuario?')) {
      this.cambiarEstado(id, 'Rechazado');
    }
  }
  
  cambiarEstado(id: string, nuevoEstado: string) {
    const token = this.authService.getToken();
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  
    this.http.put(
      `http://localhost:7000/user/${id}`,
      { estado: nuevoEstado },
      { headers }
    ).subscribe({
      next: () => {
        const usuario = this.usuarios.find(u => u.id === id);
        if (usuario) usuario.estado = nuevoEstado;
        alert(`Usuario ${nuevoEstado.toLowerCase()}`);
      },
      error: () => alert('Error al cambiar estado')
    });
  }
  
  cambiarRol(id: string, nuevoRol: string) {
    const token = this.authService.getToken();
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  
    this.http.put(
      `http://localhost:7000/user/${id}`,
      { rol: nuevoRol },
      { headers }
    ).subscribe({
      next: () => {
        const usuario = this.usuarios.find(u => u.id === id);
        if (usuario) usuario.rol = nuevoRol;
        alert(`Rol cambiado a ${nuevoRol}`);
      },
      error: () => alert('Error al cambiar rol')
    });
  }
  

  editarUsuario(id: string) {
    alert('Funcionalidad de editar en desarrollo');
  }

  eliminarUsuario(id: string) {
    if (!this.puedeEliminar()) {
      alert('Solo el administrador puede eliminar');
      return;
    }

    if (confirm('¿Eliminar este usuario?')) {
      const token = this.authService.getToken();
      const headers = new HttpHeaders({
        'Authorization': `Bearer ${token}`
      });

      this.http.delete(`http://localhost:7000/user/${id}`, { headers }).subscribe({
        next: () => {
          this.usuarios = this.usuarios.filter(u => u.id !== id);
          alert('Usuario eliminado');
        },
        error: () => alert('Error al eliminar')
      });
    }
  }
}