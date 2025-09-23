import { Component } from '@angular/core';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.html',
  styleUrl: './admin.css'
})
export class Admin {
  currentYear: number = new Date().getFullYear();
}
