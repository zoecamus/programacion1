import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../../services/auth.services';

interface Usuario {
  id: string;
  nombre: string;
  apellido: string;
  email: string;
  telefono: string;
  rol: string;
  estado: string;
}

@Component({
  selector: 'app-usuarios',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  templateUrl: './usuarios.html',
  styleUrls: ['./usuarios.css']
})
export class UsuariosComponent implements OnInit {
  private apiUrl = 'http://localhost:7000';
  
  usuarios: Usuario[] = [];
  busqueda: string = '';
  loading: boolean = true;
  error: string = '';

  constructor(
    private http: HttpClient,
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.cargarUsuarios();
  }

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  cargarUsuarios() {
    this.loading = true;
    this.http.get<Usuario[]>(`${this.apiUrl}/usuarios`, { headers: this.getHeaders() }).subscribe({
      next: (usuarios) => {
        this.usuarios = usuarios;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar usuarios:', error);
        this.error = 'Error al cargar los usuarios';
        this.loading = false;
      }
    });
  }

  get usuariosFiltrados(): Usuario[] {
    if (!this.busqueda) {
      return this.usuarios;
    }
    
    const termino = this.busqueda.toLowerCase();
    return this.usuarios.filter(u => 
      u.nombre.toLowerCase().includes(termino) || 
      u.apellido.toLowerCase().includes(termino) ||
      u.email.toLowerCase().includes(termino) ||
      u.rol.toLowerCase().includes(termino)
    );
  }

  getRolBadgeClass(rol: string): string {
    switch(rol) {
      case 'Administrador': return 'bg-danger';
      case 'Encargado': return 'bg-warning';
      case 'Cliente': return 'bg-primary';
      default: return 'bg-secondary';
    }
  }

  cambiarEstado(usuario: Usuario, nuevoEstado: string) {
    if (!this.puedeEditarEstado()) {
      alert('No tienes permisos para cambiar el estado de usuarios');
      return;
    }

    this.http.put(
      `${this.apiUrl}/usuarios/${usuario.id}/estado`, 
      { estado: nuevoEstado },
      { headers: this.getHeaders() }
    ).subscribe({
      next: () => {
        usuario.estado = nuevoEstado;
        alert('Estado actualizado correctamente');
      },
      error: (error) => {
        console.error('Error al actualizar estado:', error);
        alert('Error al actualizar el estado');
      }
    });
  }

  puedeEditarEstado(): boolean {
    const rol = this.authService.getUserRole();
    return rol === 'Administrador' || rol === 'Encargado';
  }

  editarUsuario(usuarioId: string) {
    alert('Función de edición en desarrollo');
    // Aquí iría la lógica para abrir un modal de edición
  }

  eliminarUsuario(usuarioId: string) {
    if (!this.puedeEliminar()) {
      alert('No tienes permisos para eliminar usuarios');
      return;
    }

    if (confirm('¿Estás seguro de eliminar este usuario?')) {
      this.http.delete(
        `${this.apiUrl}/usuarios/${usuarioId}`,
        { headers: this.getHeaders() }
      ).subscribe({
        next: () => {
          this.usuarios = this.usuarios.filter(u => u.id !== usuarioId);
          alert('Usuario eliminado correctamente');
        },
        error: (error) => {
          console.error('Error al eliminar usuario:', error);
          alert('Error al eliminar el usuario');
        }
      });
    }
  }

  puedeEliminar(): boolean {
    return this.authService.getUserRole() === 'Administrador';
  }

  volverDashboard() {
    const redirectUrl = this.authService.getRedirectUrl();
    this.router.navigate([redirectUrl]);
  }
}