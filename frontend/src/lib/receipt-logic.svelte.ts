import type { Item, User } from './types';

// --- Kleine Helper ---
export function getSplitSum(item: Item): number {
    if (!item.splits) return 0;
    return item.splits.reduce((sum, split) => sum + split.amount, 0);
}

export function checkIsComplete(item: Item): boolean {
    return Math.abs(item.total_price - getSplitSum(item)) < 0.01;
}

export function isUserActive(item: Item, email: string): boolean {
    return item.splits.some(s => s.user_email === email);
}

export function applyGlobalFairSplits(items: Item[]) {
    const balanceTracker: Record<string, number> = {};

    items.forEach((item) => {
        if (!item.splits || item.splits.length === 0) return;

        const totalCents = Math.round(item.total_price * 100);
        const numParticipants = item.splits.length;
        
        const shareCents = Math.trunc(totalCents / numParticipants);
        const remainderCents = totalCents % numParticipants;
        const absRemainder = Math.abs(remainderCents);
        const centSign = Math.sign(totalCents);

        const exactShare = totalCents / numParticipants; 
        item.splits.forEach(s => {
            if (balanceTracker[s.user_email] === undefined) balanceTracker[s.user_email] = 0;
            balanceTracker[s.user_email] += exactShare;
        });

        const shuffledEmails = item.splits.map(s => s.user_email)
            .sort(() => Math.random() - 0.5);

        const sortedParticipants = shuffledEmails.sort((a, b) => {
            if (centSign >= 0) {
                return balanceTracker[b] - balanceTracker[a];
            } else {
                return balanceTracker[a] - balanceTracker[b];
            }
        });

        item.splits.forEach((split) => {
            let extraCent = 0;
            if (sortedParticipants.indexOf(split.user_email) < absRemainder) {
                extraCent = centSign;
            }
            const finalAmountCents = shareCents + extraCent;
            split.amount = finalAmountCents / 100;
            balanceTracker[split.user_email] -= finalAmountCents;
        });
    });
}

export function toggleUser(item: Item, email: string, allItems: Item[]) {
    const index = item.splits.findIndex(s => s.user_email === email);
    if (index !== -1) {
        item.splits.splice(index, 1);
    } else {
        item.splits.push({ user_email: email, amount: 0 });
    }
    applyGlobalFairSplits(allItems);
}

export function toggleAll(item: Item, users: User[], allItems: Item[]) {
    if (item.splits.length === users.length) {
        item.splits = [];
    } else {
        item.splits = users.map(u => ({ user_email: u.email, amount: 0 }));
    }
    applyGlobalFairSplits(allItems);
}