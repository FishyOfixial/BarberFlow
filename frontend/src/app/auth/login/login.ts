import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class LoginComponent {
  username = '';
  password = '';

  constructor(private auth: AuthService, private router: Router) {}

  login() {
    this.auth.login(this.username, this.password).subscribe({
      next: res => {
        const role = this.auth.getRole();
        if (role === 'client') this.router.navigate(['/client']);
        else if (role === 'barber') this.router.navigate(['/barber']);
        else this.router.navigate(['/admin']);
      },
      error: err => {
        alert('Login fallido: ' + (err.error.detail || 'Verifica credenciales'));
      }
    });
  }
}
