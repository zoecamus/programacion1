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
  { path : 'productos', component: ProductosComponent },
  { path : 'pedidos', component: PedidosComponent },
  { path: 'usuarios', component: UsuariosComponent },
  
  // Dashboard adaptable según rol
  { 
    path: 'dashboard/:rol', 
    component: DashboardComponent,
    canActivate: [AuthGuard]
  },
  
  // Ruta específica de admin (tu componente actual)
  
  // Productos (accesible para admin y cliente)
  // { 
  //   path: 'productos', 
  //   component: ProductosComponent,
  //   canActivate: [AuthGuard],
  //   data: { roles: ['admin', 'cliente'] }
  // },
  
  // Pedidos (accesible para todos)
  // { 
  //   path: 'pedidos', 
  //   component: PedidosComponent,
  //   canActivate: [AuthGuard]
  // },
  
  { path: '**', redirectTo: '/login' }
];