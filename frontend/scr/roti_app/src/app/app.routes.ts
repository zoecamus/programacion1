import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login';
import { DashboardComponent } from './pages/dashboard/dashboard';
import { AuthGuard } from './guards/auth.guards';
import { ProductosComponent } from './pages/productos/productos';
import { PedidosComponent } from './pages/pedidos/pedidos';
import { UsuariosComponent } from './pages/usuarios/usuarios';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  
  // Dashboard para Administrador
  { 
    path: 'dashboard/admin', 
    component: DashboardComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Administrador'] }
  },
  
  // Dashboard para Encargado
  { 
    path: 'dashboard/encargado', 
    component: DashboardComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Encargado'] }
  },
  
  // Productos (para clientes)
  { 
    path: 'productos', 
    component: ProductosComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Cliente', 'Administrador'] }
  },
  
  // Pedidos
  { 
    path: 'pedidos', 
    component: PedidosComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Encargado', 'Administrador', 'Cliente'] }
  },
  
  // Usuarios (solo admin)
  { 
    path: 'usuarios', 
    component: UsuariosComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Administrador'] }
  },
  
  { path: '**', redirectTo: '/login' }
];