// src/lib/types.ts

export interface User {
    email: string;
    name: string;
}

export interface Split {
    user_email: string;
    amount: number;
}

export interface Item {
    name: string;
    total_price: number;
    quantity?: number;      
    unit_price?: number;    
    category?: string;      
    splits: Split[];
}

export interface ParsedData {
    title: string;
    payer_email: string;
    items: Item[];
}

export interface Transaction {
    id: string;
    title: string;
    payer_email: string;
    date: string;
    items: Item[];
}

export interface Balance {
        email: string;
        name: string;
        amount: number;
    }