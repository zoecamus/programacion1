import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, of } from 'rxjs';
import { tap, catchError, map } from 'rxjs/operators';

export type UserRole = 'admin' | 'cliente' | 'empleado';

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
  private readonly API_URL = 'http://localhost:7000/api'; // Cambiar 

  constructor(private http: HttpClient, private router: Router) {}

  login(email: string, password: string): Observable<boolean> {
    return this.http.post<User>(`${this.API_URL}/login`, { email, password }).pipe(
      tap(user => {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(user));
      }),
      map(() => true),
      catchError(() => of(false))
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
      case 'admin':
        return '/dashboard/admin';
      case 'cliente':
        return '/productos';
      case 'empleado':
        return '/pedidos';
      default:
        return '/login';
    }
  }
  private readonly USERS = [
    { email: 'admin@laroti.com', password: 'admin123', nombre: 'Admin', rol: 'admin' as UserRole },
    { email: 'cliente@laroti.com', password: 'cliente123', nombre: 'Juan Cliente', rol: 'cliente' as UserRole },
    { email: 'empleado@laroti.com', password: 'empleado123', nombre: 'Pedro Empleado', rol: 'empleado' as UserRole }
  ];
  
}
