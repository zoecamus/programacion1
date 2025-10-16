import { Routes } from '@angular/router';

// Importá todos tus componentes desde pages
import { UsuariosComponent } from './pages/usuarios/usuarios';
import { DashboardComponent } from './pages/dashboard/dashboard';
import { LoginComponent } from './pages/login/login';
import { PerfilComponent } from './pages/perfil/perfil';
import { PedidosComponent } from './pages/pedidos/pedidos';
import { ProductosComponent } from './pages/productos/productos';
import { PromocionesComponent } from './pages/promociones/promociones';
import { RegisterComponent } from './pages/registro/register';

export const routes: Routes = [
  // Ruta principal - Menú público (página de clientes)
  { 
    path: '', 
    component: ProductosComponent,  // ← Vista principal para clientes
    title: 'La Roti - Comida casera para retirar'
  },
  
  // Ruta de login
  { 
    path: 'login', 
    component: LoginComponent,
    title: 'Iniciar sesión - La Roti'
  },
  
  // Ruta de registro
  { 
    path: 'registro', 
    component: RegisterComponent,
    title: 'Registrarse - La Roti'
  },
  
  // Ruta de perfil de usuario
  { 
    path: 'perfil', 
    component: PerfilComponent,
    title: 'Mi perfil - La Roti'
  },
  
  // ✅ Ruta de MIS PEDIDOS (para clientes)
  { 
    path: 'mis-pedidos', 
    component: PedidosComponent,
    title: 'Mis pedidos - La Roti'
  },
  
  // ✅ Ruta alternativa para pedidos
  { 
    path: 'pedidos', 
    component: PedidosComponent,
    title: 'Pedidos - La Roti'
  },
  
  // Rutas de administración
  { 
    path: 'dashboard', 
    component: DashboardComponent,
    title: 'Dashboard - La Roti Admin'
  },
  
  // Alias para dashboard admin/encargado
  { 
    path: 'dashboard/admin', 
    component: DashboardComponent,
    title: 'Dashboard Admin - La Roti'
  },
  
  { 
    path: 'dashboard/encargado', 
    component: DashboardComponent,
    title: 'Dashboard Encargado - La Roti'
  },
  
  // ✅ Gestión de PEDIDOS (para admin)
  { 
    path: 'admin/pedidos', 
    component: PedidosComponent,
    title: 'Gestión de Pedidos - La Roti Admin'
  },
  
  { 
    path: 'admin/productos', 
    component: ProductosComponent,
    title: 'Gestión de Productos - La Roti Admin'
  },
  
  // ✅ Gestión de USUARIOS (para admin)
  { 
    path: 'admin/usuarios', 
    component: UsuariosComponent,
    title: 'Gestión de Usuarios - La Roti Admin'
  },
  
  { 
    path: 'admin/promociones', 
    component: PromocionesComponent,
    title: 'Promociones - La Roti Admin'
  },
  
  // Alias para admin principal
  { 
    path: 'admin', 
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  
  // Ruta 404 - Redirige al inicio
  { 
    path: '**', 
    redirectTo: '' 
  }
];