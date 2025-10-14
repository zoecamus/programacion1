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
      console.log('No está logueado, redirigiendo al login');
      this.router.navigate(['/login']);
      return false;
    }

    // Verificar roles si están definidos en la ruta
    const requiredRoles = route.data['roles'] as UserRole[];
    
    if (requiredRoles && requiredRoles.length > 0) {
      const userRole = this.authService.getUserRole();
      console.log('Rol del usuario:', userRole);
      console.log('Roles requeridos:', requiredRoles);
      
      if (!userRole || !requiredRoles.includes(userRole)) {
        console.log('No tiene permiso, redirigiendo');
        // Redirigir a su página correspondiente
        this.router.navigate([this.authService.getRedirectUrl()]);
        return false;
      }
    }

    console.log('Acceso permitido');
    return true;
  }
}