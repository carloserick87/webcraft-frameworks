import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-navbar',
  imports: [],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css',
})
export class Navbar {

topMenu = {
  home: 'Home',
  about: 'About Us',
  place: 'Coworking',
  events: 'Events',
  contact: 'Contact'
}

bookCategories = {
  fiction: 'Fiction',
  nonFiction: 'Non-fiction',
  mysteryThriller: 'Mystery & Thriller',
  romance: 'Romance',
  scienceFiction: 'Science Fiction',
  fantasy: 'Fantasy',
  horror: 'Horror',
  drama: 'Drama',
  adventure: 'Adventure',
  childrensBooks: "Children's Books",
  academicBooks: 'Academic Books'
}



}
