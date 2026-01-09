import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css'],
})
export class LoginComponent {
  email = '';
  password = '';

  constructor(private auth: AuthService) {}

  login() {
    this.auth.login(this.email, this.password).subscribe(res => {
      this.auth.saveToken(res.access);
      alert('Login exitoso');
    });
  }
}
