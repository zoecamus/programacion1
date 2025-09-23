import { Component } from '@angular/core';

@Component({
  selector: 'app-usuario',
  imports: [],
  templateUrl: './usuario.html',
  styleUrls: ['./usuario.css']
})
export class Usuario {
  currentYear: number = new Date().getFullYear();
}
