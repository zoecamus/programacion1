import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, of } from 'rxjs';
import { tap, catchError, map } from 'rxjs/operators';

export type UserRole = 'Administrador' | 'Encargado' | 'Cliente';

export interface User {
  email: string;
  nombre: string;
  rol: UserRole;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly STORAGE_KEY = 'currentUser';
  private readonly API_URL = 'http://localhost:7000/auth'; // Cambiar 

  constructor(private http: HttpClient, private router: Router) {}

  login(email: string, password: string): Observable<boolean> {
    console.log('🔵 Enviando login a:', `${this.API_URL}/login`);
    console.log('🔵 Datos:', { email, password });
    
    return this.http.post<User>(`${this.API_URL}/login`, { email, password }).pipe(
      tap(user => {
        console.log('✅ Respuesta exitosa:', user);
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(user));
      }),
      map(() => true),
      catchError((error) => {
        console.error('❌ Error completo:', error);
        console.error('❌ Status:', error.status);
        console.error('❌ Error body:', error.error);
        return of(false);
      })
    );
  }
  logout() {
    localStorage.removeItem(this.STORAGE_KEY);
    this.router.navigate(['/login']);
  }

  getCurrentUser(): User | null {
    const userData = localStorage.getItem(this.STORAGE_KEY);
    return userData ? JSON.parse(userData) : null;
  }

  isLoggedIn(): boolean {
    return this.getCurrentUser() !== null;
  }

  hasRole(roles: UserRole[]): boolean {
    const user = this.getCurrentUser();
    return user ? roles.includes(user.rol) : false;
  }

  getUserRole(): UserRole | null {
    const user = this.getCurrentUser();
    return user ? user.rol : null;
  }

  getRedirectUrl(): string {
    const rol = this.getUserRole();
    switch (rol) {
      case 'Administrador':
        return '/dashboard/admin';
      case 'Encargado':
        return '/dashboard/encargado';
      case 'Cliente':
        return '/productos';
      default:
        return '/login';
    }
  }}
