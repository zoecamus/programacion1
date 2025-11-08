import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home';  
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
  // ✅ LANDING PAGE - PÚBLICA (sin AuthGuard)
  { path: '', component: HomeComponent },
  
  // ✅ LOGIN Y REGISTRO - PÚBLICOS
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  
  // ✅ ESPERA CONFIRMACIÓN - Sin AuthGuard porque ya está logueado
  { 
    path: 'espera-confirmacion', 
    component: EsperaConfirmacionComponent
  },

  // ✅ RUTAS PROTEGIDAS - Requieren autenticación
  
  // Dashboard (Admin, Encargado, Empleado)
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
  
  // Productos (Cliente, Admin, Encargado)
  { 
    path: 'productos', 
    component: ProductosComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Cliente', 'Administrador', 'Encargado'] }
  },
  
  // Pedidos (Todos los roles autenticados)
  { 
    path: 'pedidos', 
    component: PedidosComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Encargado', 'Administrador', 'Cliente'] }
  },
  
  // Valoración (Solo clientes)
  { 
    path: 'valoracion', 
    component: ValoracionComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Cliente'] }
  },
  
  // Mi Cuenta (Solo clientes)
  { 
    path: 'mi-cuenta', 
    component: MiCuentaComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Cliente'] }
  },
  
  // Usuarios (Admin y Encargado)
  { 
    path: 'usuarios', 
    component: UsuariosComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Administrador', 'Encargado'] }
  },
  
  // Promociones (Admin, Encargado, Cliente)
  { 
    path: 'promociones', 
    component: PromocionesComponent,
    canActivate: [AuthGuard],
    data: { roles: ['Administrador', 'Encargado', 'Cliente'] }
  },
  
  // ✅ RUTA POR DEFECTO - Si no encuentra la ruta, redirige al home
  { path: '**', redirectTo: '' }
];