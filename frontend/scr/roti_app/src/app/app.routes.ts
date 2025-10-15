import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login';
import { DashboardComponent } from './pages/dashboard/dashboard';
import { AuthGuard } from './guards/auth.guards';
import { ProductosComponent } from './pages/productos/productos';
import { PedidosComponent } from './pages/pedidos/pedidos';
import { UsuariosComponent } from './pages/usuarios/usuarios';
import { PromocionesComponent } from './pages/promociones/promociones';  
import { RegisterComponent } from './pages/registro/register';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },

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
    path: 'usuarios', 
    component: UsuariosComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Administrador', 'Encargado'] }
  },
  
  { 
    path: 'promociones', 
    component: PromocionesComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Administrador', 'Encargado'] }
  },
  
  { path: '**', redirectTo: '/login' }
];