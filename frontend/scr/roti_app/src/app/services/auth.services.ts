import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

// ✅ Exportar el tipo de roles
export type UserRole = 'Administrador' | 'Encargado' | 'Cliente';

// ✅ Interface para el usuario
export interface User {
  id: string;
  email: string;
  nombre: string;
  apellido?: string;
  telefono?: string;
  rol: UserRole;
}

// ✅ Interface para la respuesta del login
export interface LoginResponse {
  id: string;
  email: string;
  nombre: string;
  rol: UserRole;
  access_token: string;
}

// ✅ Injectable y exportado
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:7000/auth'; // ✅ Cambiar a puerto 7000

  constructor(private http: HttpClient) {}

  /**
   * Realiza el login y guarda los datos en localStorage
   */
  login(email: string, password: string): Observable<boolean> {
    console.log('🔵 AuthService: Enviando login...');
    
    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, { email, password })
      .pipe(
        map(response => {
          console.log('✅ Respuesta del servidor:', response);
          
          // Guarda TODOS los datos en localStorage
          localStorage.setItem('token', response.access_token);
          localStorage.setItem('rol', response.rol);
          localStorage.setItem('email', response.email);
          localStorage.setItem('nombre', response.nombre);
          localStorage.setItem('userId', response.id);
          
          console.log('💾 Datos guardados en localStorage');
          console.log('👤 Rol del usuario:', response.rol);
          
          return true;
        }),
        catchError(error => {
          console.error('❌ Error en login:', error);
          return of(false);
        })
      );
  }

  /**
   * Registra un nuevo usuario
   */
  register(usuario: any): Observable<boolean> {
    return this.http.post(`${this.apiUrl}/register`, usuario)
      .pipe(
        map(() => true),
        catchError(error => {
          console.error('Error en registro:', error);
          return of(false);
        })
      );
  }

  /**
   * Determina la URL de redirección según el rol del usuario
   */
  getRedirectUrl(): string {
    const rol = this.getUserRole();
    console.log('🎯 Calculando redirección para rol:', rol);
    
    switch (rol) {
      case 'Administrador':
        return '/dashboard/admin';
      case 'Encargado':
        return '/dashboard/encargado';
      case 'Cliente':
        return '/productos';
      default:
        console.warn('⚠️ Rol desconocido:', rol);
        return '/productos';
    }
  }

  /**
   * Verifica si el usuario está autenticado
   */
  isLoggedIn(): boolean {
    const hasToken = !!localStorage.getItem('token');
    console.log('🔐 isLoggedIn:', hasToken);
    return hasToken;
  }

  /**
   * Alias de isLoggedIn para compatibilidad
   */
  isAuthenticated(): boolean {
    return this.isLoggedIn();
  }

  /**
   * Obtiene el rol del usuario actual
   */
  getUserRole(): UserRole | null {
    const rol = localStorage.getItem('rol') as UserRole | null;
    console.log('👤 getUserRole:', rol);
    return rol;
  }

  /**
   * Alias de getUserRole
   */
  getRole(): UserRole | null {
    return this.getUserRole();
  }

  /**
   * Obtiene el token del usuario actual
   */
  getToken(): string | null {
    return localStorage.getItem('token');
  }

  /**
   * Obtiene el email del usuario actual
   */
  getEmail(): string | null {
    return localStorage.getItem('email');
  }

  /**
   * Obtiene el nombre del usuario actual
   */
  getNombre(): string | null {
    return localStorage.getItem('nombre');
  }

  /**
   * Obtiene el ID del usuario actual
   */
  getUserId(): string | null {
    return localStorage.getItem('userId');
  }

  /**
   * Cierra la sesión del usuario
   */
  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('rol');
    localStorage.removeItem('email');
    localStorage.removeItem('nombre');
    localStorage.removeItem('userId');
    console.log('👋 Sesión cerrada');
  }

  /**
   * Limpia todos los datos de la sesión
   */
  clearSession(): void {
    this.logout();
  }

  /**
   * Obtiene toda la información del usuario actual
   */
  getCurrentUser(): User | null {
    const token = this.getToken();
    
    if (!token) {
      console.log('❌ No hay usuario logueado');
      return null;
    }

    const user: User = {
      id: localStorage.getItem('userId') || '',
      email: localStorage.getItem('email') || '',
      nombre: localStorage.getItem('nombre') || '',
      apellido: localStorage.getItem('apellido') || undefined,
      telefono: localStorage.getItem('telefono') || undefined,
      rol: localStorage.getItem('rol') as UserRole
    };

    console.log('👤 getCurrentUser:', user);
    return user;
  }
}