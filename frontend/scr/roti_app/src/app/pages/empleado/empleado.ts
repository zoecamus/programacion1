import { Component } from '@angular/core';

@Component({
  selector: 'app-empleado',
  standalone: true,
  templateUrl: './empleado.html',
  styleUrls: ['./empleado.css']
})
export class Empleado {
  currentYear: number = new Date().getFullYear();
}


