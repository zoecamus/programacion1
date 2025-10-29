import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login';
import { DashboardComponent } from './pages/dashboard/dashboard';
import { AuthGuard } from './guards/auth.guards';
import { ProductosComponent } from './pages/productos/productos';
import { PedidosComponent } from './pages/pedidos/pedidos';
import { UsuariosComponent } from './pages/usuarios/usuarios';
import { PromocionesComponent } from './pages/promociones/promociones';  
import { RegisterComponent } from './pages/registro/register';
import { ValoracionComponent } from './pages/valoraciones/valoracion';
import { MiCuentaComponent } from './pages/mi_cuenta/mi_cuenta';
import { EsperaConfirmacionComponent } from './pages/espera_confirmacion.py/espera_confirmacion';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  
  // ← AGREGAR ruta de espera (sin AuthGuard porque el usuario ya está logueado)
  { 
    path: 'espera-confirmacion', 
    component: EsperaConfirmacionComponent
  },

  // Ruta general de dashboard (para todos los roles)
  { 
    path: 'dashboard', 
    component: DashboardComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Administrador', 'Encargado', 'Empleado'] }
  },

  { 
    path: 'dashboard/admin', 
    component: DashboardComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Administrador'] }
  },
  
  { 
    path: 'dashboard/encargado', 
    component: DashboardComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Encargado'] }
  },
  
  { 
    path: 'productos', 
    component: ProductosComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Cliente', 'Administrador', 'Encargado'] }
  },
  
  { 
    path: 'pedidos', 
    component: PedidosComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Encargado', 'Administrador', 'Cliente'] }
  },
  
  { 
    path: 'valoracion', 
    component: ValoracionComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Cliente'] }
  },
  
  { 
    path: 'mi-cuenta', 
    component: MiCuentaComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Cliente'] }
  },
  
  { 
    path: 'usuarios', 
    component: UsuariosComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Administrador', 'Encargado'] }
  },
  
  { 
    path: 'promociones', 
    component: PromocionesComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Administrador', 'Encargado', 'Cliente'] }
  },
  
  { path: '**', redirectTo: '/login' }
];