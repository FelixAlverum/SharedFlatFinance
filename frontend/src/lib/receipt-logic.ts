import type { User, Item, ParsedData, Split } from '$lib/types';

export function toggleUser(item: Item, email: string) {
        let activeEmails = item.splits.map(s => s.user_email);
        
        if (activeEmails.includes(email)) {
            activeEmails = activeEmails.filter(e => e !== email); 
        } else {
            activeEmails.push(email); 
        }
        recalculateEqualSplits(item, activeEmails);
    }

export function toggleAll(item: Item, users:User[]) {
        const activeEmails = item.splits.map(s => s.user_email);
        
        if (activeEmails.length === users.length) {
            recalculateEqualSplits(item, []);
        } else {
            const allEmails = users.map(u => u.email);
            recalculateEqualSplits(item, allEmails);
        }
    }

export function isUserActive(item: Item, email: string): boolean {
        return item.splits.some(s => s.user_email === email);
    }

export function checkIsComplete(item: Item): boolean {
        return Math.abs(item.total_price - getSplitSum(item)) < 0.01; 
    }

export function getSplitSum(item: Item) {
        return item.splits.reduce((sum, split) => sum + split.amount, 0);
    }

export function recalculateEqualSplits(item: Item, activeEmails: string[]) {
        if (activeEmails.length === 0) {
            item.splits = [];
            return;
        }
        const amount = Math.round((item.total_price / activeEmails.length) * 100) / 100;
        item.splits = activeEmails.map(email => ({ user_email: email, amount }));
        
        const sum = amount * activeEmails.length;
        const diff = Math.round((item.total_price - sum) * 100) / 100;
        if (diff !== 0) {
            item.splits[0].amount = Math.round((item.splits[0].amount + diff) * 100) / 100;
        }
    }