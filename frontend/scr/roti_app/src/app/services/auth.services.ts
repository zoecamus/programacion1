import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { Observable } from 'rxjs';

export type UserRole = 'Administrador' | 'Cliente' | 'Empleado' | 'Encargado';

export interface User {
  email: string;
  nombre?: string;
  rol?: UserRole;
  access_token?: string;
  id?: string;
  estado?: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly STORAGE_KEY = 'currentUser';
  private readonly API_URL = 'http://localhost:7000/auth/login';

  constructor(private http: HttpClient, private router: Router) {}

  /**
   * Decodifica el payload de un JWT (sin verificar firma)
   */
  private decodeToken(token: string): any {
    try {
      const payload = token.split('.')[1];
      const decoded = atob(payload);
      return JSON.parse(decoded);
    } catch (e) {
      console.error('Error al decodificar token:', e);
      return null;
    }
  }

  /**
   * Inicia sesión con el backend y guarda el token en localStorage
   */
  login(email: string, password: string): Observable<boolean> {
    return this.http.post<any>(this.API_URL, { email, password }).pipe(
      tap(response => {
        console.log('🔵 Respuesta del backend:', response);
        
        if (response && response.access_token) {
          // ✅ Decodificar el token para obtener rol, nombre, estado
          const tokenData = this.decodeToken(response.access_token);
          
          console.log('🔓 Token decodificado:', tokenData);
          
          const userData: User = {
            email: response.email,
            id: response.email,
            access_token: response.access_token,
            nombre: tokenData?.nombre,
            rol: tokenData?.rol || null,
            estado: tokenData?.estado || 'Activo'
          };
          
          localStorage.setItem(this.STORAGE_KEY, JSON.stringify(userData));
          console.log('✅ Usuario guardado en localStorage:', userData);
          
          // Redirigir automáticamente según el rol Y el estado
          const redirectUrl = this.getRedirectUrl();
          console.log('🚀 Redirigiendo a:', redirectUrl);
          this.router.navigate([redirectUrl]);
        }
      }),
      tap(() => true),
      tap({
        error: (err) => {
          console.error('❌ Error en login:', err);
          return false;
        }
      })
    );
  }

  /**
   * Cierra sesión y redirige al login
   */
  logout() {
    localStorage.removeItem(this.STORAGE_KEY);
    this.router.navigate(['/login']);
  }

  /**
   * Obtiene el usuario actual desde localStorage
   */
  getCurrentUser(): User | null {
    const userData = localStorage.getItem(this.STORAGE_KEY);
    return userData ? JSON.parse(userData) : null;
  }

  /**
   * Devuelve true si hay usuario autenticado
   */
  isLoggedIn(): boolean {
    return this.getCurrentUser() !== null;
  }

  /**
   * Devuelve el rol del usuario actual
   */
  getUserRole(): UserRole | null {
    const user = this.getCurrentUser();
    return user ? user.rol || null : null;
  }

  getEmail(): string | null {
    const user = this.getCurrentUser();
    return user ? user.email : null;
  }
  
  /**
   * Devuelve el token del usuario actual
   */
  getToken(): string | null {
    const user = this.getCurrentUser();
    return user ? user.access_token || null : null;
  }

  /**
   * Redirige al dashboard según el rol Y el estado
   */
  getRedirectUrl(): string {
    const user = this.getCurrentUser();
    const rol = user?.rol;
    const estado = user?.estado;
    
    console.log('🔍 Rol del usuario:', rol, 'Estado:', estado);
    
    // Si el usuario está pendiente de aprobación, redirigir a espera
    if (estado === 'Pendiente') {
      return '/espera-confirmacion';
    }
    
    // Si el usuario está bloqueado, cerrar sesión
    if (estado === 'Bloqueado') {
      alert('Tu cuenta está bloqueada. Contacta al administrador.');
      this.logout();
      return '/login';
    }
    
    switch (rol) {
      case 'Administrador':
        return '/dashboard';
      case 'Encargado':
        return '/dashboard';
      case 'Empleado':
        return '/dashboard';
      case 'Cliente':
        return '/productos';
      default:
        return '/login';
    }
  }

  register(payload: any) {
    return this.http.post<any>('http://localhost:7000/auth/register', payload);
  }
  
  /**
   * Obtiene info del usuario desde el backend usando el token
   * Útil para refrescar datos sin hacer login
   */
  getMe(): Observable<User> {
    return this.http.get<User>('http://localhost:7000/auth/me');
  }
}