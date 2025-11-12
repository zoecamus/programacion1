import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

/**
 * Interceptor de autenticación para La Roti
 * 
 * Este interceptor automáticamente:
 * 1. Agrega el token JWT a todas las peticiones HTTP (excepto login y register)
 * 2. Maneja errores 401 (token expirado o inválido)
 * 3. Redirige al login cuando el token es inválido
 * 4. Limpia el localStorage cuando hay errores de autenticación
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  
  // Lista de URLs que NO necesitan token (login, register, etc.)
  const excludedUrls = [
    '/login',
    '/register',
    '/auth/login',
    '/auth/register'
  ];
  
  // Verificar si la URL actual debe ser excluida
  const shouldExclude = excludedUrls.some(url => req.url.includes(url));
  
  // Si la URL está en la lista de exclusión, continuar sin agregar token
  if (shouldExclude) {
    console.log('🔓 Request sin token (URL excluida):', req.url);
    return next(req);
  }
  
  // Obtener el token del localStorage desde currentUser
  let token: string | null = null;
  const currentUser = localStorage.getItem('currentUser');
  if (currentUser) {
    try {
      const userData = JSON.parse(currentUser);
      token = userData.access_token || null;
    } catch (e) {
      console.error('Error al parsear currentUser:', e);
    }
  }
  
  // Preparar la request (con o sin token)
  let clonedRequest = req;
  
  if (token) {
    // Clonar la request y agregar el header Authorization con el token
    clonedRequest = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
    console.log('🔐 Token agregado a la petición:', req.url);
  } else {
    console.warn('⚠️ No hay token disponible para:', req.url);
  }
  
  // Ejecutar la petición y manejar errores
  return next(clonedRequest).pipe(
    catchError((error: HttpErrorResponse) => {
      // Manejar error 401 (No autorizado - token inválido o expirado)
      if (error.status === 401) {
        console.error('❌ Error 401: Token inválido o expirado');
        console.log('🔄 Limpiando sesión y redirigiendo al login...');
        
        // Limpiar el localStorage
        localStorage.removeItem('currentUser');
        
        // Redirigir al login
        router.navigate(['/login'], {
          queryParams: { 
            returnUrl: router.url,
            reason: 'session-expired' 
          }
        });
      }
      
      // Manejar error 403 (Forbidden - sin permisos)
      if (error.status === 403) {
        console.error('❌ Error 403: Acceso denegado');
        // Opcional: redirigir a una página de "sin permisos"
      }
      
      // Re-lanzar el error para que los componentes puedan manejarlo
      return throwError(() => error);
    })
  );
};
