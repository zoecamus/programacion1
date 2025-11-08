import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
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

interface PaginationInfo {
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

@Component({
  selector: 'app-usuarios',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './usuarios.html',
  styleUrls: ['./usuarios.css']
})
export class UsuariosComponent implements OnInit {
  
  usuarios: Usuario[] = [];
  loading = false;
  error = '';
  
  // ✅ FILTROS (se envían al backend)
  busqueda = '';
  rolFiltro = '';
  estadoFiltro = '';
  Math = Math;
  
  // ✅ PAGINACIÓN (viene del backend)
  pagination: PaginationInfo = {
    total: 0,
    page: 1,
    per_page: 10,
    total_pages: 0,
    has_next: false,
    has_prev: false
  };

  private readonly API_URL = 'http://localhost:7000';

  constructor(
    private http: HttpClient,
    private router: Router,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.cargarUsuarios();
  }

  /**
   * ✅ CARGAR USUARIOS DEL BACKEND CON FILTROS Y PAGINACIÓN
   */
  cargarUsuarios() {
    this.loading = true;
    this.error = '';

    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    // ✅ CONSTRUIR QUERY PARAMS
    const params: any = {
      page: this.pagination.page.toString(),
      per_page: this.pagination.per_page.toString()
    };

    if (this.busqueda.trim()) {
      params.busqueda = this.busqueda.trim();
    }

    if (this.rolFiltro) {
      params.rol = this.rolFiltro;
    }

    if (this.estadoFiltro) {
      params.estado = this.estadoFiltro;
    }

    console.log('📡 Cargando usuarios con params:', params);

    this.http.get<any>(`${this.API_URL}/users`, { headers, params }).subscribe({
      next: (response) => {
        console.log('✅ Respuesta del backend:', response);
        this.usuarios = response.usuarios || [];
        this.pagination = response.pagination || this.pagination;
        this.loading = false;
      },
      error: (error) => {
        console.error('❌ Error al cargar usuarios:', error);
        this.error = error.error?.error || 'Error al cargar usuarios';
        this.loading = false;
      }
    });
  }

  /**
   * ✅ APLICAR FILTROS (resetea a página 1 y recarga)
   */
  aplicarFiltros() {
    this.pagination.page = 1; // Resetear a página 1 al filtrar
    this.cargarUsuarios();
  }

  /**
   * ✅ LIMPIAR FILTROS
   */
  limpiarFiltros() {
    this.busqueda = '';
    this.rolFiltro = '';
    this.estadoFiltro = '';
    this.pagination.page = 1;
    this.cargarUsuarios();
  }

  /**
   * ✅ CAMBIAR PÁGINA
   */
  cambiarPagina(page: number) {
    if (page >= 1 && page <= this.pagination.total_pages) {
      this.pagination.page = page;
      this.cargarUsuarios();
    }
  }

  /**
   * ✅ CAMBIAR ITEMS POR PÁGINA
   */
  cambiarPerPage(perPage: number) {
    this.pagination.per_page = perPage;
    this.pagination.page = 1; // Resetear a página 1
    this.cargarUsuarios();
  }

  /**
   * Cambiar rol de usuario
   */
  cambiarRol(usuarioId: string, nuevoRol: string) {
    if (!this.puedeCambiarRol()) {
      alert('No tienes permisos para cambiar roles');
      return;
    }

    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.put(
      `${this.API_URL}/user/${usuarioId}`,
      { rol: nuevoRol },
      { headers }
    ).subscribe({
      next: () => {
        console.log('✅ Rol actualizado');
        this.cargarUsuarios();
      },
      error: (error) => {
        console.error('❌ Error al cambiar rol:', error);
        alert('Error al cambiar rol: ' + (error.error?.error || 'Error desconocido'));
        this.cargarUsuarios();
      }
    });
  }

  /**
   * Cambiar estado de usuario
   */
  cambiarEstado(usuarioId: string, nuevoEstado: string) {
    if (!this.puedeEditarEstado()) {
      alert('No tienes permisos para cambiar estados');
      return;
    }

    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.put(
      `${this.API_URL}/user/${usuarioId}`,
      { estado: nuevoEstado },
      { headers }
    ).subscribe({
      next: () => {
        console.log('✅ Estado actualizado');
        this.cargarUsuarios();
      },
      error: (error) => {
        console.error('❌ Error al cambiar estado:', error);
        alert('Error al cambiar estado: ' + (error.error?.error || 'Error desconocido'));
        this.cargarUsuarios();
      }
    });
  }

  /**
   * Aprobar usuario (Pendiente → Activo)
   */
  aprobarUsuario(usuarioId: string) {
    this.cambiarEstado(usuarioId, 'Activo');
  }

  /**
   * Rechazar usuario (Pendiente → Bloqueado)
   */
  rechazarUsuario(usuarioId: string) {
    if (confirm('¿Estás seguro de rechazar este usuario?')) {
      this.cambiarEstado(usuarioId, 'Bloqueado');
    }
  }

  /**
   * Eliminar usuario (solo Admin)
   */
  eliminarUsuario(usuarioId: string) {
    if (!confirm('¿Estás seguro de eliminar este usuario? Esta acción no se puede deshacer.')) {
      return;
    }

    const token = this.authService.getToken();
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.delete(`${this.API_URL}/user/${usuarioId}`, { headers }).subscribe({
      next: () => {
        console.log('✅ Usuario eliminado');
        this.cargarUsuarios();
      },
      error: (error) => {
        console.error('❌ Error al eliminar:', error);
        alert('Error al eliminar usuario: ' + (error.error?.error || 'Error desconocido'));
      }
    });
  }

  /**
   * Permisos
   */
  esAdmin(): boolean {
    return this.authService.getUserRole() === 'Administrador';
  }

  puedeCambiarRol(): boolean {
    return this.esAdmin();
  }

  puedeEditarEstado(): boolean {
    const rol = this.authService.getUserRole();
    return rol === 'Administrador' || rol === 'Encargado';
  }

  puedeGestionarUsuarios(): boolean {
    return this.puedeEditarEstado();
  }

  /**
   * Volver al dashboard
   */
  volverDashboard() {
    this.router.navigate(['/dashboard']);
  }

  /**
   * Generar array de números de página para paginación
   */
  get paginas(): number[] {
    const pages: number[] = [];
    const current = this.pagination.page;
    const total = this.pagination.total_pages;
    
    // Mostrar 5 páginas alrededor de la actual
    let start = Math.max(1, current - 2);
    let end = Math.min(total, current + 2);
    
    // Ajustar si hay menos de 5 páginas
    if (end - start < 4) {
      if (start === 1) {
        end = Math.min(total, start + 4);
      } else {
        start = Math.max(1, end - 4);
      }
    }
    
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    
    return pages;
  }
}