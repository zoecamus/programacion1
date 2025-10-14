import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService, UserRole } from '../services/auth.services';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  
  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot): boolean {
    // Verificar si está logueado
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return false;
    }

    // Verificar roles si están definidos en la ruta
    const requiredRoles = route.data['roles'] as UserRole[];
    if (requiredRoles && !this.authService.hasRole(requiredRoles)) {
      // Redirigir a su página correspondiente
      this.router.navigate([this.authService.getRedirectUrl()]);
      return false;
    }

    return true;
  }
}