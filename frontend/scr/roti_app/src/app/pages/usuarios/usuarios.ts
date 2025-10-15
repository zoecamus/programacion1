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
  estado?: 'Activo' | 'Bloqueado' | 'Pendiente';
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

  // Modal
  mostrarModal: boolean = false;
  usuarioEditando: Usuario | null = null;

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.currentUserRole = this.authService.getUserRole();
    this.cargarUsuarios();
  }

  private getHeaders(): HttpHeaders {
    const user = localStorage.getItem('currentUser');
    const token = user ? JSON.parse(user).access_token : '';
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  cargarUsuarios() {
    this.loading = true;
    this.error = '';
    
    console.log('🔵 Cargando usuarios...');
    
    this.http.get<any>('http://localhost:7000/users', { headers: this.getHeaders() }).subscribe({
      next: (response) => {
        console.log('✅ Usuarios recibidos:', response);
        this.usuarios = response.usuarios || response;
        this.loading = false;
      },
      error: (err) => {
        console.error('❌ Error al obtener usuarios:', err);
        this.error = 'Error al cargar usuarios. Verifica los permisos.';
        this.loading = false;
      }
    });
  }
    
  get usuariosFiltrados(): Usuario[] {
    const termino = this.busqueda.toLowerCase();
    return this.usuarios.filter(u =>
      u.nombre.toLowerCase().includes(termino) ||
      u.email.toLowerCase().includes(termino) ||
      u.rol.toLowerCase().includes(termino)
    );
  }
   
  getRolBadgeClass(rol: string): string {
    switch(rol) {
      case 'Administrador': return 'text-bg-danger';
      case 'Encargado': return 'text-bg-info';
      case 'Cliente': return 'text-bg-primary';
      default: return 'text-bg-secondary';
    }
  }
    
  cambiarEstado(usuario: Usuario, nuevoEstado: 'Activo' | 'Bloqueado' | 'Pendiente') {
    if (confirm(`¿Cambiar estado de ${usuario.nombre} a "${nuevoEstado}"?`)) {
      this.http.put(
        `http://localhost:7000/user/${usuario.id}`,
        { estado: nuevoEstado },
        { headers: this.getHeaders() }
      ).subscribe({
        next: () => {
          usuario.estado = nuevoEstado;
          alert(`Estado actualizado a "${nuevoEstado}"`);
        },
        error: (err) => {
          console.error('Error al cambiar estado:', err);
          alert('Error al cambiar el estado');
        }
      });
    }
  }

  editarUsuario(id: string) {
    const usuario = this.usuarios.find(u => u.id === id);
    if (usuario) {
      this.usuarioEditando = { ...usuario };
      this.mostrarModal = true;
    }
  }

  eliminarUsuario(id: string) {
    if (this.currentUserRole !== 'Administrador') {
      alert('Solo el administrador puede eliminar usuarios');
      return;
    }

    if (confirm('¿Estás seguro de eliminar este usuario?')) {
      this.http.delete(
        `http://localhost:7000/user/${id}`,
        { headers: this.getHeaders() }
      ).subscribe({
        next: () => {
          this.usuarios = this.usuarios.filter(u => u.id !== id);
          alert('Usuario eliminado correctamente');
        },
        error: (err) => {
          console.error('Error al eliminar:', err);
          alert('Error al eliminar usuario');
        }
      });
    }
  }

  cerrarModal() {
    this.mostrarModal = false;
    this.usuarioEditando = null;
  }

  guardarCambios() {
    if (!this.usuarioEditando) return;

    this.http.put(
      `http://localhost:7000/user/${this.usuarioEditando.id}`,
      this.usuarioEditando,
      { headers: this.getHeaders() }
    ).subscribe({
      next: () => {
        const index = this.usuarios.findIndex(u => u.id === this.usuarioEditando!.id);
        if (index !== -1) {
          this.usuarios[index] = { ...this.usuarioEditando! };
        }
        alert('Usuario actualizado correctamente');
        this.cerrarModal();
      },
      error: (err) => {
        console.error('Error al actualizar:', err);
        alert('Error al actualizar usuario');
      }
    });
  }

  volverDashboard() {
    const redirectUrl = this.authService.getRedirectUrl();
    this.router.navigate([redirectUrl]);
  }

  puedeEditarEstado(): boolean {
    return this.currentUserRole === 'Administrador' || this.currentUserRole === 'Encargado';
  }

  puedeEliminar(): boolean {
    return this.currentUserRole === 'Administrador';
  }
}