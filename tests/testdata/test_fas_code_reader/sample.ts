//@ts-ignore
import * as fs from 'fs';
//@ts-ignore
import { EventEmitter } from 'events';
//@ts-ignore
import axios from 'axios';          
//@ts-ignore
import { format } from 'date-fns'; 
//@ts-ignore
import { Connection } from 'typeorm'; 

declare function print(...args: any[]): void;

for (let i: number = 0; i < 10; i++) {
    for (let j: number = 0; j < 10; j++) {
        print(i, j);
    }
}