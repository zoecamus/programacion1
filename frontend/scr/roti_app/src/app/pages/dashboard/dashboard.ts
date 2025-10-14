import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService, UserRole } from '../../services/auth.services';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class DashboardComponent implements OnInit {
  userRole: UserRole | null = null;
  userName: string = '';

  constructor(
    public authService: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    const user = this.authService.getCurrentUser();
    if (user) {
      this.userRole = user.rol;
      this.userName = user.nombre;
    }
  }

  navigateTo(route: string) {
    this.router.navigate([route]);
  }

  logout() {
    this.authService.logout();
  }
}